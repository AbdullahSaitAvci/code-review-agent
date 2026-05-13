// Kasıtlı hatalı JavaScript kodu
var userData = null;
var MAX = 100;

function processData(x, y, z) {
  var result = x * 3.14159;
  if (result > MAX) {
    for (var i = 0; i < 10; i++) {
      for (var j = 0; j < 10; j++) {
        if (i + j > 15) {
          result = result + i * j - 2.71828;
        }
      }
    }
  }
  return result;
}