<template>
  <v-container class="body-upload-pages">

    <div class="excel-container">
      <v-card class="upload-card">
        <v-card-title>Uploader un fichier Excel</v-card-title>
        <v-card-text>
          <v-file-input v-model="excelFile" label="Choisissez un fichier Excel" show-size
                        accept=".xlsx, .xls" @change="handleExcelUpload"></v-file-input>

          <div class="file-container" v-if="excelPreview">
            <div class="file-item">
              <v-icon>mdi-file-excel-box</v-icon>
              <span>{{ excelPreview.name }}</span>
              <v-btn icon @click="removeExcelFile">
                <v-icon>mdi-close</v-icon>
              </v-btn>
            </div>
          </div>
        </v-card-text>
      </v-card>

      <v-card v-if="excelData.length">
        <v-infinite-scroll :items="visibleRows" @load="loadMoreRows">
          <v-table fixed-header height="400px">
            <thead>
            <tr>
              <th v-for="(header, index) in excelData[0]" :key="'header-' + index">
                {{ header }}
              </th>
            </tr>
            </thead>
            <tbody>
            <tr v-for="(row, rowIndex) in visibleRows" :key="'row-' + rowIndex">
              <td v-for="(cell, colIndex) in row" :key="'cell-' + rowIndex + '-' + colIndex">
                {{ cell }}
              </td>
            </tr>
            </tbody>
          </v-table>
        </v-infinite-scroll>
      </v-card>


    </div>


  </v-container>
</template>

<script src="./script_upload.js"></script>

<style scoped>
.v-card {
  border-radius: 8px;
}
.body-upload-pages{
  width: 100rem;
  height: 100vh;
}
.upload-card{
  justify-content: center;
  margin-top: 10rem;
}
</style>
