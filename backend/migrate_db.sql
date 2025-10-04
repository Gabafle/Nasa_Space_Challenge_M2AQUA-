-- Add new columns to datasets table
ALTER TABLE datasets 
ADD COLUMN original_filename VARCHAR(255) NOT NULL DEFAULT '',
ADD COLUMN is_public BOOLEAN DEFAULT FALSE;

-- Update existing records if needed
UPDATE datasets SET original_filename = filename WHERE original_filename = '';
