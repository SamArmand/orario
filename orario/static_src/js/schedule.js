var dayNum = function(day) {
//  var lower_day = day.toLowerCase();
  switch(day.toLowerCase()) {
    case 'monday':
      return 0;
    case 'tuesday':
      return 1;
    case 'wednesday':
      return 2;
    case 'thursday':
      return 3;
    case 'friday':
      return 4;
    case 'saturday':
      return 5;
    case 'sunday':
      return 6;
    case undefined || null:
      return 'your argument is non-existant'
    default:
      return 'your argument is invalid';
    
  }
}

var addSlot = function(day,begin,end, name) {
  var height = end - begin;
  var offset = (begin - 8)/15*20;
  var dayIndex = dayNum(day);
  var day = document.querySelectorAll('.day')[dayNum];
  var d = document.querySelectorAll('.d')[dayNum];
  var bigNode = document.createElement('div');
  var smallNode = document.createElement('div');
  
  bigNode.setAttribute('style','top:'+offset+ 'px;'+ 'height:'+height +'px;');
  bigNode.className += 'container big-d-col';
  bigNode.innerText = name;
  smallNode.setAttribute('style','top:'+offset+ 'px;' + 'height:'+height/2 +'px;');
  smallNode.className += 'container small-d-col';
  smallNode.innerText = name;
  day.appendChild(bigNode);
  d.appendChild(smallNode);
  console.log('slot added');
}




//var binToDay = function(binstr) {
//  switch(binstr) {
//    case '0000001':
//      return
//  }
//}