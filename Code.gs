function doGet() {
  var html = UrlFetchApp.fetch('https://aldumestani.github.io/student-photo-review/?v=' + new Date().getTime()).getContentText();
  return HtmlService.createHtmlOutput(html).setTitle('مطابقة صور الطلبة').setXFrameOptionsMode(HtmlService.XFrameOptionsMode.ALLOWALL);
}

function doPost(e) {
  try {
    var data = JSON.parse(e.postData.contents);
    var sheet = SpreadsheetApp.getActiveSpreadsheet().getActiveSheet();
    var teacher = data.teacher || "غير معروف";
    
    if (sheet.getLastRow() === 0) {
      sheet.appendRow(["التاريخ", "اسم المدرس", "رقم الصورة", "اسم الطالب", "الشعبة"]);
    }
    
    var allData = sheet.getDataRange().getValues();
    var rowsToKeep = [allData[0]];
    for (var i = 1; i < allData.length; i++) {
      if (allData[i][1] !== teacher) {
        rowsToKeep.push(allData[i]);
      }
    }
    
    var matches = data.matches || {};
    var classMap = getClassMap();
    var now = new Date();
    
    for (var photo in matches) {
      var name = matches[photo];
      var cls = classMap[name] || "";
      rowsToKeep.push([now, teacher, photo, name, cls]);
    }
    
    sheet.clear();
    if (rowsToKeep.length > 0) {
      sheet.getRange(1, 1, rowsToKeep.length, 5).setValues(rowsToKeep);
    }
    
    return ContentService
      .createTextOutput(JSON.stringify({status: "ok", count: Object.keys(matches).length}))
      .setMimeType(ContentService.MimeType.JSON);
  } catch (err) {
    return ContentService
      .createTextOutput(JSON.stringify({status: "error", message: err.toString()}))
      .setMimeType(ContentService.MimeType.JSON);
  }
}

function getClassMap() {
  var map = {};
  var sheet = SpreadsheetApp.getActiveSpreadsheet().getSheetByName("اسماء الطلبة");
  if (!sheet) return map;
  var data = sheet.getDataRange().getValues();
  for (var i = 1; i < data.length; i++) {
    map[data[i][0]] = data[i][1];
  }
  return map;
}
