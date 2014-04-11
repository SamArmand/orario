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

var addSlots = function(json) {
//  Need to access these vars: dayString,begin,end,name
//  FAAAIL
//  var dayIndex = dayNum(day);
//  var day = document.querySelectorAll('.day')[dayNum];
//  var d = document.querySelectorAll('.d')[dayNum];
  // This should be an array

  var days = decodeDays(dayString);
  days.forEach(function(element, index) {
    var height = slotLength(begin,end);
    var offset = (parseTime(begin).getHours - 8)/15*20; //not sure about this

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
  });

}




//var binToDay = function(binstr) {
//  switch(binstr) {
//    1 '0000001':monday
//    2 '0000010':tuesday
//    4 '0000100':wednesday
//    8 '0001000':thursday
//    16 '0010000':friday
//    32 '0100000':saturday
//    64 '1000010':sunday
//  }
//}


///////////////////////////////////////////>
//\\\\ ROBOT UNICORNS ////////////////
///////////////////////////


//Parse Time- You made this? I made this
function parseTime(timeStr, dt) {
    if (!dt) {
        dt = new Date();
    }

    var time = timeStr.match(/(\d+)(?::(\d\d))?\s*(p?)/i);
    if (!time) {
        return NaN;
    }
    var hours = parseInt(time[1], 10);
    if (hours == 12 && !time[3]) {
        hours = 0;
    }
    else {
        hours += (hours < 12 && time[3]) ? 12 : 0;
    }

    dt.setHours(hours);
    dt.setMinutes(parseInt(time[2], 10) || 0);
    dt.setSeconds(0, 0);
    return dt;
}


//Beast function
var iterate = function(object) {
  for (var key in object) {
    if (typeof object[key] == 'object') {
      if (key == 'lecture'){
        console.log('A WILD LECTURE HAS APPEARED');
      }
      console.log('---------NEW OBJECT:'+ key +'----------');
      iterate(object[key]);
      console.log('--------END OF OBJECT--------');
    }
    else {
      console.log(key+ ': ' +object[key]);
    }
  }
}

// Turn binary DaysString into discreet days)
var decodeDays = function(dayInt) {
  // ex: 10
  var days = [];
  var M=1,T=2,W=4,J=8,F=16,S=32,D=64;

  if (dayInt & M) { days.push(0);}
  if (dayInt & T) { days.push(1);}
  if (dayInt & W) { days.push(2);}
  if (dayInt & J) { days.push(3);}
  if (dayInt & F) { days.push(4);}
  if (dayInt & S) { days.push(5);}
  if (dayInt & D) { days.push(6);}
  return days;
}

//returns minute span of a slot
var slotLength = function(start,stop) {
  var _start = parseTime(start);
  var startmins = (_start.getHours() *60) + _start.getMinutes();
  var _stop = parseTime(stop);
  var stopmins = (_stop.getHours() * 60) + _stop.getMinutes() ;

  var height = stopmins - startmins;
  return height;

}


var render = function(timeSlot,courseNumber) {

  var begin_time = parseTime(timeSlot.begin_time);
  var begin_min = begin_time.getHours() * 60 + begin_time.getMinutes();
  var end_time = parseTime(timeSlot.end_time);
  var end_min = end_time.getHours() * 60 + end_time.getMinutes();
  var name = '<h4>'+courseNumber+'</h4><p>'+begin_time.toTimeString().substring(0,5)+'&mdash;'+end_time.toTimeString().substring(0,5)+'</p>';
  if (timeSlot.room)
    name += '<p>'+timeSlot.room+'</p>';
  var height = (end_min - begin_min)/15 * 20;
  var offset =(begin_min/15*20)-(8*60/15*20) + 37//begin_min - 320 +14;
  console.log('rendering timeslot:',begin_time,begin_min,end_time,end_min,height,offset);
//  var height = slotLength(begin,end);
//  var offset = (parseTime(begin).getHours - 8)/15*20; //not sure about this
  // days determines the number of slots to add
  var days = decodeDays(timeSlot.days);
  days.forEach(function(day) {
    var DOMday = document.getElementsByClassName('day')[day];
    var DOMd = document.getElementsByClassName('d')[day];
    var bigNode = document.createElement('div');
    var smallNode = document.createElement('div');

    bigNode.setAttribute('style','top:'+offset+ 'px;'+ 'height:'+height +'px;' + 'background-color:'+'cornflowerblue;'+'color:'+'white');
    bigNode.className += 'container big-d-col';
    bigNode.innerHTML = name;
    smallNode.setAttribute('style','top:'+offset+ 'px;' + 'height:'+height/2 +'px;' + 'background-color:'+'cornflowerblue;'+'color:'+'white');
    smallNode.className += 'container small-d-col';
    smallNode.innerHTML = name;
    DOMday.appendChild(bigNode);
    DOMd.appendChild(smallNode);
    console.log('slot added');
    })
};



////////////////////////
var main = function(){
  console.log('all sections');
  //j.sections - Array - section objects containing lec, tut,lab objects
  j.sections.forEach(function(el,i) {
    var section = el;
    var course = section.course.number;
    render(section.lecture,course);
    if (section.tutorial) {
      render(section.tutorial,course);
    }
    if (section.lab) {
      render(section.lab,course);
    }
  j.busyslots.forEach(function(el,i) {
    var slot = el;
    render(slot, slot.label);
  })
})


};

