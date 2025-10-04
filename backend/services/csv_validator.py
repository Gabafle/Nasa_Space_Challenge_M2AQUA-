import pandas as pd
import numpy as np
import os
import json
import re
from datetime import datetime
from typing import Dict, List, Any, Optional, Tuple

class CSVValidationResult:
    def __init__(self):
        self.valid = True
        self.errors = []
        self.warnings = []
        self.summary = {}
        self.detailed_report = ""

class EnhancedCSVValidator:
    def __init__(self):
        self.suspicious_values = ['N/A', 'n/a', 'null', 'NULL', 'None', '#N/A', '#NULL!', 'undefined', '', ' ', '-', 'NaN', 'nan']
        self.max_errors_shown = 3
        
    def validate_csv_file(self, filepath: str, filename: str) -> CSVValidationResult:
        """Comprehensive CSV validation with detailed error reporting"""
        result = CSVValidationResult()
        
        try:
            # Try multiple encodings
            df = None
            encodings = ['utf-8', 'latin-1', 'cp1252', 'iso-8859-1', 'utf-16']
            used_encoding = None
            
            for encoding in encodings:
                try:
                    df = pd.read_csv(filepath, encoding=encoding, low_memory=False)
                    used_encoding = encoding
                    break
                except UnicodeDecodeError:
                    continue
                except Exception as e:
                    result.errors.append({
                        'line': 0,
                        'column': '',
                        'error': f'Failed to read CSV with {encoding}: {str(e)}',
                        'value': '',
                        'severity': 'critical'
                    })
            
            if df is None:
                result.valid = False
                result.errors.append({
                    'line': 0,
                    'column': '',
                    'error': 'Could not read file with any supported encoding',
                    'value': '',
                    'severity': 'critical'
                })
                return result
            
            # Basic file checks
            if df.empty:
                result.valid = False
                result.errors.append({
                    'line': 0,
                    'column': '',
                    'error': 'CSV file is completely empty',
                    'value': '',
                    'severity': 'critical'
                })
                return result
            
            # Update summary
            result.summary = {
                'total_rows': len(df),
                'total_columns': len(df.columns),
                'encoding_used': used_encoding,
                'file_size_bytes': os.path.getsize(filepath),
                'missing_values': df.isnull().sum().sum(),
                'duplicate_rows': df.duplicated().sum()
            }
            
            # Check for empty rows
            self._check_empty_rows(df, result)
            
            # Check for duplicate column names
            self._check_duplicate_columns(df, result)
            
            # Check data type consistency
            self._check_data_type_consistency(df, result)
            
            # Check for suspicious null-like values
            self._check_suspicious_values(df, result)
            
            # Check for special characters and encoding issues
            self._check_encoding_issues(df, result)
            
            # Generate detailed report
            result.detailed_report = self._generate_detailed_report(result, filename)
            
            # Final validation status
            result.valid = len([e for e in result.errors if e.get('severity') == 'critical']) == 0
            
            return result
            
        except Exception as e:
            result.valid = False
            result.errors.append({
                'line': 0,
                'column': '',
                'error': f'Unexpected error during validation: {str(e)}',
                'value': '',
                'severity': 'critical'
            })
            return result
    
    def _check_empty_rows(self, df: pd.DataFrame, result: CSVValidationResult):
        """Check for completely empty rows"""
        empty_rows = df.isnull().all(axis=1)
        empty_row_indices = empty_rows[empty_rows].index.tolist()
        
        for idx in empty_row_indices[:10]:  # Limit to first 10
            result.errors.append({
                'line': idx + 2,  # +2 for header and 1-based indexing
                'column': 'all',
                'error': 'Completely empty row detected',
                'value': '',
                'severity': 'error'
            })
        
        if len(empty_row_indices) > 10:
            result.warnings.append({
                'line': 0,
                'column': '',
                'error': f'Found {len(empty_row_indices)} empty rows in total',
                'value': ''
            })
    
    def _check_duplicate_columns(self, df: pd.DataFrame, result: CSVValidationResult):
        """Check for duplicate column names"""
        if len(df.columns) != len(set(df.columns)):
            duplicated_cols = df.columns[df.columns.duplicated()].tolist()
            for col in set(duplicated_cols):
                result.errors.append({
                    'line': 1,
                    'column': col,
                    'error': f'Duplicate column name detected: "{col}"',
                    'value': col,
                    'severity': 'critical'
                })
    
    def _check_data_type_consistency(self, df: pd.DataFrame, result: CSVValidationResult):
        """Check for data type inconsistencies within columns"""
        for col in df.columns:
            non_null_data = df[col].dropna()
            if len(non_null_data) == 0:
                continue
                
            # Sample data for analysis (max 1000 rows for performance)
            sample_data = non_null_data.head(min(1000, len(non_null_data)))
            
            numeric_count = 0
            string_count = 0
            date_count = 0
            inconsistent_entries = []
            
            for idx, value in sample_data.items():
                str_value = str(value).strip()
                
                # Skip suspicious null-like values for type checking
                if str_value.lower() in [v.lower() for v in self.suspicious_values]:
                    continue
                
                is_numeric = self._is_numeric(str_value)
                is_date = self._is_date_like(str_value)
                
                if is_numeric:
                    numeric_count += 1
                elif is_date:
                    date_count += 1
                else:
                    string_count += 1
                    
                # Collect inconsistent entries
                if len(inconsistent_entries) < 5:
                    if numeric_count > 0 and not is_numeric and not is_date:
                        inconsistent_entries.append({
                            'line': idx + 2,
                            'value': str_value,
                            'expected': 'numeric'
                        })
            
            # Determine if there are type inconsistencies
            total_typed = numeric_count + string_count + date_count
            if total_typed > 10:  # Only check columns with sufficient data
                if numeric_count > total_typed * 0.7 and string_count > 0:
                    # Mostly numeric but has strings
                    for entry in inconsistent_entries[:3]:
                        result.errors.append({
                            'line': entry['line'],
                            'column': col,
                            'error': f'Non-numeric value "{entry["value"]}" in predominantly numeric column',
                            'value': entry['value'],
                            'severity': 'error'
                        })
    
    def _check_suspicious_values(self, df: pd.DataFrame, result: CSVValidationResult):
        """Check for suspicious null-like values"""
        for col in df.columns:
            suspicious_found = []
            for idx, value in df[col].items():
                if str(value).strip() in self.suspicious_values:
                    if len(suspicious_found) < 3:
                        suspicious_found.append({
                            'line': idx + 2,
                            'value': str(value)
                        })
            
            if suspicious_found:
                for entry in suspicious_found:
                    result.warnings.append({
                        'line': entry['line'],
                        'column': col,
                        'error': f'Suspicious null-like value found: "{entry["value"]}"',
                        'value': entry['value']
                    })
    
    def _check_encoding_issues(self, df: pd.DataFrame, result: CSVValidationResult):
        """Check for encoding issues and special characters"""
        for col in df.columns:
            for idx, value in df[col].head(100).items():  # Check first 100 rows
                str_value = str(value)
                if '�' in str_value or len(str_value.encode('utf-8')) != len(str_value.encode('utf-8', errors='ignore')):
                    result.warnings.append({
                        'line': idx + 2,
                        'column': col,
                        'error': 'Possible encoding issue or special characters detected',
                        'value': str_value[:50] + '...' if len(str_value) > 50 else str_value
                    })
                    break  # Only report first occurrence per column
    
    def _is_numeric(self, value: str) -> bool:
        """Check if value is numeric (int or float)"""
        try:
            float(value.replace(',', ''))
            return True
        except (ValueError, TypeError):
            return False
    
    def _is_date_like(self, value: str) -> bool:
        """Check if value looks like a date"""
        date_patterns = [
            r'\d{4}-\d{2}-\d{2}',
            r'\d{2}/\d{2}/\d{4}',
            r'\d{2}-\d{2}-\d{4}',
            r'\d{4}/\d{2}/\d{2}'
        ]
        return any(re.match(pattern, value.strip()) for pattern in date_patterns)
    
    def _generate_detailed_report(self, result: CSVValidationResult, filename: str) -> str:
        """Generate comprehensive error report"""
        report_lines = [
            f"CSV Validation Report for: {filename}",
            f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            "=" * 60,
            "",
            "SUMMARY:",
            f"File Status: {'✓ PASSED' if result.valid else '✗ FAILED'}",
            f"Total Rows: {result.summary.get('total_rows', 0):,}",
            f"Total Columns: {result.summary.get('total_columns', 0)}",
            f"File Size: {result.summary.get('file_size_bytes', 0):,} bytes",
            f"Encoding Used: {result.summary.get('encoding_used', 'Unknown')}",
            f"Missing Values: {result.summary.get('missing_values', 0):,}",
            f"Duplicate Rows: {result.summary.get('duplicate_rows', 0):,}",
            f"Critical Errors: {len([e for e in result.errors if e.get('severity') == 'critical'])}",
            f"Errors: {len([e for e in result.errors if e.get('severity') == 'error'])}",
            f"Warnings: {len(result.warnings)}",
            ""
        ]
        
        # Add critical errors
        critical_errors = [e for e in result.errors if e.get('severity') == 'critical']
        if critical_errors:
            report_lines.extend([
                "CRITICAL ERRORS (Must be fixed):",
                "-" * 40
            ])
            for i, error in enumerate(critical_errors, 1):
                report_lines.append(f"{i}. Line {error['line']}, Column '{error['column']}':")
                report_lines.append(f"   {error['error']}")
                if error['value']:
                    report_lines.append(f"   Value: '{error['value']}'")
                report_lines.append("")
        
        # Add regular errors
        regular_errors = [e for e in result.errors if e.get('severity') == 'error']
        if regular_errors:
            report_lines.extend([
                "ERRORS (Should be fixed):",
                "-" * 30
            ])
            for i, error in enumerate(regular_errors, 1):
                report_lines.append(f"{i}. Line {error['line']}, Column '{error['column']}':")
                report_lines.append(f"   {error['error']}")
                if error['value']:
                    report_lines.append(f"   Value: '{error['value']}'")
                report_lines.append("")
        
        # Add warnings
        if result.warnings:
            report_lines.extend([
                "WARNINGS (Recommended to review):",
                "-" * 35
            ])
            for i, warning in enumerate(result.warnings, 1):
                report_lines.append(f"{i}. Line {warning['line']}, Column '{warning['column']}':")
                report_lines.append(f"   {warning['error']}")
                if warning.get('value'):
                    report_lines.append(f"   Value: '{warning['value']}'")
                report_lines.append("")
        
        # Add recommendations
        report_lines.extend([
            "RECOMMENDATIONS:",
            "- Fix all critical errors before proceeding",
            "- Review and address regular errors for better data quality", 
            "- Consider warnings for optimal data processing",
            "- Ensure consistent data types within columns",
            "- Remove or properly handle missing/null values",
            "- Use consistent date formats if applicable",
            "- Avoid special characters that might cause encoding issues"
        ])
        
        return "\n".join(report_lines)
