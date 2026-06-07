function doPost(e) {
  try {
    var data = JSON.parse(e.postData.contents);
    var sheet = SpreadsheetApp.getActiveSpreadsheet().getActiveSheet();
    
    // Ensure header row
    if (sheet.getLastRow() === 0) {
      sheet.appendRow(["التاريخ", "رقم الصورة", "اسم الطالب", "الشعبة"]);
    }
    
    var matches = data.matches || {};
    var rows = [];
    var classMap = getClassMap();
    
    for (var photo in matches) {
      var name = matches[photo];
      var cls = classMap[name] || "";
      rows.push([new Date(), photo, name, cls]);
    }
    
    if (rows.length > 0) {
      sheet.getRange(sheet.getLastRow() + 1, 1, rows.length, 4).setValues(rows);
    }
    
    return ContentService
      .createTextOutput(JSON.stringify({status: "ok", count: rows.length}))
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
