import * as XLSX from 'xlsx';

export default {
  data() {
    return {
      excelFile: null,
      excelPreview: null,
      excelData: [],
      visibleRows: [],
      currentIndex: 1,
      chunkSize: 50,
    };
  },
  methods: {
    handleExcelUpload() {
      const file = Array.isArray(this.excelFile) ? this.excelFile[0] : this.excelFile;

      if (file) {
        this.excelPreview = {
          name: file.name,
          type: 'excel',
        };

        const reader = new FileReader();
        reader.onload = (e) => {
          const data = new Uint8Array(e.target.result);
          const workbook = XLSX.read(data, { type: 'array' });
          const firstSheet = workbook.Sheets[workbook.SheetNames[0]];
          const sheetData = XLSX.utils.sheet_to_json(firstSheet, { header: 1 });

          this.excelData = sheetData;
          this.resetVisibleRows();
        };
        reader.readAsArrayBuffer(file);
      } else {
        this.removeExcelFile();
      }
    },


    resetVisibleRows() {
      this.currentIndex = 1; // Skip header row
      this.visibleRows = [];
      this.loadMoreRows({ done: () => {} });
    },

    loadMoreRows({ done }) {
      const nextRows = this.excelData.slice(this.currentIndex, this.currentIndex + this.chunkSize);
      if (nextRows.length > 0) {
        this.visibleRows.push(...nextRows);
        this.currentIndex += this.chunkSize;
        done('ok');
      } else {
        done('empty'); // Nothing left to load
      }
    },

    removeExcelFile() {
      this.excelFile = null;
      this.excelPreview = null;
      this.excelData = [];
      this.visibleRows = [];
    },

  },
};
