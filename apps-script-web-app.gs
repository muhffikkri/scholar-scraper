/**
 * Google Apps Script Web App untuk menerima data dari aplikasi desktop
 * dan menulis ke Google Spreadsheet
 *
 * Deployment:
 * 1. Buka Google Apps Script (script.google.com)
 * 2. Buat project baru
 * 3. Copy-paste code ini
 * 4. Deploy > New Deployment > Web App
 * 5. Execute as: Me
 * 6. Who has access: Anyone
 * 7. Copy Web App URL
 */

/**
 * Fungsi ini berjalan ketika permintaan HTTP POST diterima oleh Web App.
 * Ia menerima data publikasi dan menuliskannya ke spreadsheet yang ditentukan.
 * @param {Object} e - Objek event yang berisi parameter permintaan.
 */
function doPost(e) {
  try {
    // 1. Parse data JSON yang dikirim dari Python
    const requestData = JSON.parse(e.postData.contents);

    // 2. Ekstrak parameter yang diperlukan dari request
    const spreadsheetId = requestData.spreadsheetId;
    const sheetName = requestData.sheetName;
    const data = requestData.data; // Data ini diharapkan berupa array 2D (list of lists)

    // Validasi input
    if (!spreadsheetId || !sheetName || !data || !Array.isArray(data)) {
      throw new Error("Parameter 'spreadsheetId', 'sheetName', atau 'data' tidak valid atau hilang.");
    }

    // 3. Buka spreadsheet target menggunakan ID-nya
    const spreadsheet = SpreadsheetApp.openById(spreadsheetId);

    // 4. Dapatkan sheet target berdasarkan nama. Jika tidak ada, buat baru.
    let sheet = spreadsheet.getSheetByName(sheetName);
    if (!sheet) {
      sheet = spreadsheet.insertSheet(sheetName);
    }

    // 5. Bersihkan sheet dan tulis data baru
    sheet.clear();
    const numRows = data.length;
    const numCols = data[0] ? data[0].length : 0;

    if (numRows > 0 && numCols > 0) {
      sheet.getRange(1, 1, numRows, numCols).setValues(data);
    }

    // 6. Kirim respons sukses kembali ke Python
    return ContentService.createTextOutput(
      JSON.stringify({
        status: "success",
        message: `Data berhasil ditulis ke sheet '${sheetName}'.`,
        rowsWritten: numRows,
        columnsWritten: numCols,
      })
    ).setMimeType(ContentService.MimeType.JSON);
  } catch (error) {
    // 7. Jika terjadi error, kirim respons error kembali ke Python
    Logger.log(error.toString()); // Catat error untuk debugging
    return ContentService.createTextOutput(
      JSON.stringify({
        status: "error",
        message: error.toString(),
      })
    ).setMimeType(ContentService.MimeType.JSON);
  }
}

/**
 * Fungsi test untuk development dan debugging
 * Gunakan ini untuk memastikan script bekerja dengan benar sebelum deployment
 */
function testDoPost() {
  const testData = {
    postData: {
      contents: JSON.stringify({
        spreadsheetId: "YOUR_SPREADSHEET_ID_HERE", // Ganti dengan ID spreadsheet test Anda
        sheetName: "TestSheet",
        data: [
          ["Nama Dosen", "Judul", "Penulis", "Tahun", "Sitasi"],
          ["Bambang Riyanto", "Machine Learning Research", "Bambang Riyanto, et al.", "2023", "15"],
          ["Siti Nurhaliza", "Data Mining Applications", "Siti Nurhaliza, Ahmad", "2022", "10"],
          ["Ahmad Dahlan", "Deep Learning Methods", "Ahmad Dahlan", "2024", "8"],
        ],
      }),
    },
  };

  const result = doPost(testData);
  Logger.log(result.getContent());
}
