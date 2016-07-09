var posts = new Object();
var users = new Object();
var filtered = new Object();
var lastLoad = 0;
var lastPost = 0;

// these are the error codes that can be returned from the server.
var errors = new Object();
errors['100'] = 'Yo, you should log in.';
errors['119'] = 'Your file should be an image.';
errors['121'] = 'Only whitespace makes me sad.';
errors['124'] = 'Slow down there, kiddo.';
errors['125'] = 'You should get a username.';
errors['126'] = 'That username is just not valid. At all.';
errors['127'] = 'That username can\'t be used.  For reasons.';
errors['128'] = 'If it can\'t be said in 9 letters, it\'s probably not worth saying.';
errors['129'] = 'Bad name - just numbers, letters, hyphens, or underscores.';
errors['999'] = 'That link is too big.';

////////////////////////////////////////////////////////////////////////////////
////////////////////////////////////////////////////////////////////////////////
// Ajax Functions - these functions are used for communication to the server.
////////////////////////////////////////////////////////////////////////////////
////////////////////////////////////////////////////////////////////////////////
/*
This function will send data to the server in an Ajax request.  It handles the 
creation of the XML HTTP object and submission of parameters.

The arguments are:
= params: an object with parameter-name => value mappings
= toUrl: the URL this should send to
= callbackFunction: a function to call when the response is received.  This 
  function is only called after the readyState is 4. The function will be 
  called with the original XML HTTP object and params object as parameters.
*/
function sendData(params, toUrl, callbackFunction) {
  var xmlHttp = new XMLHttpRequest();
  xmlHttp.onreadystatechange = function() {
    if (xmlHttp.readyState == 4) {
      callbackFunction(xmlHttp, params);
    }
  }
  var parameters = '';
  for (var param in params) {
    parameters += param + '=' + escape(params[param]) + '&';
  }
  xmlHttp.open("POST", toUrl, true);
  xmlHttp.setRequestHeader('Content-Type', 'application/x-www-form-urlencoded');
  xmlHttp.send(parameters);
}

/*
Send the username that a user chose in the original form field.  This code
retrieves the username from that field, performs some validity checks, and 
submits the value via Ajax.
*/
function sendUsername() {
  var text = getFormValue('username');
  if (text) {
    text = text.toLowerCase();
    for (var i = 0; i < text.length; i++) {
      var c = text.charCodeAt(i);
      if (!((c > 47 && c < 58) || (c > 96 && c < 123) || (c == 95) || (c == 45))) {
        showAlert('');
        text = '';
        break;
      }
    }
    if (text != '') {
      sendData({'username': text}, '/setuser', handleUsername);
    }
  }
}

/*
Handle the response from setting the username.  If everything is OK, we just
reload the page.  This shouldn't be called directly and is called as a response
from sendUsername().

The arguments are:
= xmlHttp - the original xmlHttp object from the Ajax request.
= params - the parameters from the Ajax request.
*/
function handleUsername(xmlHttp, params) {
  if (xmlHttp.responseText == 'OK') {
    setTimeout("loadPage('/');", 300);
  } else {
    showError(xmlHttp.responseText);
  }
}

/*
Send the post message from the user.  This function will retrieve the value 
from the text box and submit an Ajax request to the server.
*/
function sendMessage() {
  var text = getFormValue('message');
  if (text) {
    if (text.length > 9) {
      showAlert('128');
    } else {
      clearText('message');
      sendData({'text': text}, '/create', handleMessage);
    }
  }
}

/*
Respond to the sendMessage requests.  We're just going to try to reload the 
posts since they're out of date now (based on the fact that the user just
submitted one).

The arguments are:
= xmlHttp - the original xmlHttp object from the Ajax request.
= params - the parameters from the Ajax request.
*/
function handleMessage(xmlHttp) {
  if (xmlHttp.responseText != 'OK') {
    showError(xmlHttp.responseText);
  }
  setTimeout('loadPosts()', 300);
}

/*
Load the posts from the server using an Ajax request.  The "since" argument is 
supplied with the latest posts loaded from the server, so that the server can 
return an empty response if there have been no newer posts.
*/
function loadPosts() {
  sendData({'since':lastPost}, '/posts', handlePosts);
}

/*
Handle the response data from the Ajax request in the loadPosts function.  Note
that this should not be called directly.

The arguments are:
= xmlHttp - the original xmlHttp object from the Ajax request.
= params - the parameters from the Ajax request.
*/
function handlePosts(xmlHttp, params) {
  var pageData = JSON.parse(xmlHttp.responseText);
  handlePageData(pageData);
}

/*
This is the function to handle clicks on the colors in the user color 
selection table.  It sends an Ajax request to the server.

The arguments are:
= background - the background color to send.
= foreground - the foreground color to send.
*/
function handleColorSelection(background, foreground) {
  sendData({'foreground': foreground, 'background': background}, '/setcolors', handleColorChange);
}

/*
Handle the response from the Ajax request and update the selected colors on the
screen.  This function should not be called directly, but as a response to the
handleColorSelection function.


The arguments are:
= xmlHttp - the original xmlHttp object from the Ajax request.
= params - the parameters from the Ajax request.
*/
function handleColorChange(xmlHttp, params) {
  if (xmlHttp.responseText == 'OK') {
    setStyle('yourcolors', 'background-color', params['background']);
    setStyle('yourcolors', 'color', params['foreground']);
  } else {
    showError(xmlHttp.responseText);
  }
}

////////////////////////////////////////////////////////////////////////////////
////////////////////////////////////////////////////////////////////////////////
// Utility Functions - these functions are generic and can be used in any 
// application.
////////////////////////////////////////////////////////////////////////////////
////////////////////////////////////////////////////////////////////////////////
/*
Swap 2 values in an array.

The arguments are:
= array - the array in which to swap values
= i0 - the first position to swap
= i1 - the second position to swap.
*/
function swap(array, i0, i1) {
  var temp = array[i0];
  array[i0] = array[i1];
  array[i1] = temp;
}

/*
Set the HTML content of the tag specified by the ID parameter.

The arguments are:
= id - the ID of the HTML element
= text - the HTML text to set for this element.
*/
function setHtml(id, text) {
  var tag = document.getElementById(id);
  if (tag) {
    tag.innerHTML = text;
  }
}

/*
Set a style attribute for a specified HTML element.

The arguments are:
= id - the ID of the HTML element to set.
= attribute - the style attribute to modify.
= value - the new value for the style attribute.
*/
function setStyle(id, attribute, value) {
  var tag = document.getElementById(id);
  if (tag) {
    tag.style[attribute] = value;
  }
}

/*
Show the HTML element specified by the ID.  You can use this to make an HTML
element visible and optionally set its position relative to another element.

The arguments are:
= id - the ID of the HTML element to show.
= relativeTo (optional) - the element to position the other element near.
*/
function show(id, relativeTo) {
  setStyle(id, 'display', 'block');
  if (relativeTo) {
    setPositionRelativeTo(id, relativeTo);
  }
}

/* 
This function is used to create a random hex color code.  This is used in the
user color selection table.
*/
function getRandomColor() {
  var result = '#';
  for (var i = 0; i < 6; i++) {
    result += Math.floor(Math.random() * 16).toString(16);
  }
  return result;
}

/*
Hide the specified HTML element.

The arguments are:
= id - the HTML element ID to hide.
*/
function hide(id) {
  setStyle(id, 'display', 'none');
}

/*
Retrieve the text value of the specified form element.

The arguments are:
= id - the ID of the HTML form field to retrieve text from.
*/
function getFormValue(id) {
  var result = null;
  var tag = document.getElementById(id);
  if (tag) {
    return tag.value;
  }
  return result;
}

/*
Clear the text from the specified form element.

The arguments are:
= id - the ID of the HTML form field to clear the text from.
*/
function clearText(id) {
  var tag = document.getElementById(id);
  if (tag) {
    tag.value = '';
    tag.focus();
  }
}

/*
Load the page specified in the argument.

The arguments are:
= link - the link to reload.
*/
function loadPage(link) {
  document.location = link;
}

/*
Set the position relative to another component.  The "toSet" element will be 
positioned so that its top-left corner will be directly under the middle of the
"relativeTo" element.

The arguments are:
= toSet - the ID of the HTML element for which to set the position.
= relativeTo - the ID of the HTML element to move the "toSet" element near.
*/
function setPositionRelativeTo(toSet, relativeTo) {
  if (relativeTo) {
    var tag = document.getElementById(relativeTo);
    if (tag) {
      var offsets = tag.getBoundingClientRect();
      setStyle(toSet, 'left', offsets.left + (offsets.width / 2));
      setStyle(toSet, 'top', offsets.top + offsets.height);
    }
  }
}

/*
Get a text representation of the amount of time passed since the argument
"time" and now.

The arguments are:
= time - the original time for this text.
*/
function getRelativeTime(time) {
  var result = 'more than a day ago';
  var now = new Date().getTime();
  var d = (now - time) / 1000;
  if (d < 60) {
    // less than a minute
    result = 'a few seconds ago';
  } else if (d < (60 * 30)) {
    // less than 30 minutes
    var minutes = Math.round(d / 60);
    if (minutes == 1) {
      result = '1 minute ago';
    } else {
      result = minutes + ' minutes ago';
    }
  } else if (d < (60 * 60)) {
    // less than an hour
    result = 'less than an hour ago';
  } else if (d < (24 * 60 * 60)) {
    // less than a day
    var hours = Math.round(d / (60 * 60));
    if (hours == 1) {
      result = '1 hour ago';
    } else {
      result = hours + ' hours ago';
    }
  }
  return result;
}

/* 
Utility function that will return a 2-character string given a a number - 
ultimately this function pads a leading zero if necessary.

The arguments are:
= value - the value to pad with a leading zero.
*/
function pad(value) {
  var result = "" + value;
  if (value < 10) {
    result = "0" + result;
  }
  return result;
}

/*
Utility function for formatting an epoch timestamp to a YYYY-MM-DD HH:MM:SS 
value.

The arguments are:
= time - the time to format to a string.
*/
function formatTime(time) {
  var d = new Date(time);
  var result = d.getFullYear() + "-" + pad(d.getMonth() + 1) + "-" + pad(d.getDate());
  result += " " + pad(d.getHours()) + ":" + pad(d.getMinutes()) + ":" + pad(d.getSeconds());
  return result;
}

////////////////////////////////////////////////////////////////////////////////
////////////////////////////////////////////////////////////////////////////////
// UI / Application Functions - these are specific to this application's 
// functionality and user interface.
////////////////////////////////////////////////////////////////////////////////
////////////////////////////////////////////////////////////////////////////////
/*
Build a color table - this is used in the user color selection table.  This 
will insert the color table full of random colors into the specified HTML 
element ID.

The arguments are:
= id - the HTML element ID where the table should be inserted.
*/
function insertColorTable(id) {
  var text = '<table>';
  for (var i = 0; i < 6; i++) {
    text += ('<tr>');
    for (var k = 0; k < 6; k++) {
      var fg = getRandomColor();
      var bg = getRandomColor();
      text += '<td><div onclick="handleColorSelection(';
      text += "'" + bg + "',";
      text += "'" + fg + "'";
      text += ');" style="padding: 5px; font-weight: bold; background-color: ';
      text += bg + '; color: ' + fg + ';">color</div></td>';
    }
    text += ('</tr>');
  }
  text += '</table>';
  setHtml(id, text);
}

/*
Show the error specified by the code.  Show the actual code if it's not 
known.

The arguments are:
= code - the error code for which to show a message.
*/
function showError(code) {
  if (errors[code]) {
    showAlert(errors[code]);
  } else {
    showAlert('Unknown error: ' + code);
  }
}

/*
Show an alert dialog in the page with the specified message.  This will be
displayed near the logo on the page.

The arguments are:
= words - the message to display to the user.
*/
function showAlert(words) {
  var text = words + '<br><br><i>click this box to dismiss</i>';
  setHtml('dialog', text);
  show('dialog', "logo");
}

/*
Show the popup containing details on the post (username, time posted).  This
uses the "popup" HTML element in the page.

The arguments are:
= key - the post key for which to show details.
*/
function showPostDetail(key) {
  var post = posts[key];
  var text = 'By <a href="/u/' + escape(post.user.n) + '">' + post.user.n;
  text += '</a><br>';
  text += getRelativeTime(post.time) + ' at ' + formatTime(post.time) + '<br>';
  setHtml('popup-content', text);
  show('popup', key);
}

/*
Convert a post object to an HTML span.

The arguments are:
= post - the post to convert.
*/
function convertPostToHtml(post) {
  var text = '<span class="post" id="' + post.key + '" style="color: ';
  text += post.user.fg;
  text += '; background-color: ';
  text += post.user.bg;
  text += ';" onclick="showPostDetail(\'' + post.key + '\');">';
  text += post.text + '</span> ';
  return text;
}

/*
Create HTML span tags for the users and load the resulting text into the "users"
element.
*/
function loadUserArea() {
  var text = '';
  for (var i in users) {
    text += '<span id="u_' + i + '">';
    text += '<span onclick="loadPage(\'/u/' + i + '\');" class="userlink" style="color: ';
    text += users[i].fg;
    text += '; background-color: ';
    text += users[i].bg;
    text += ';">' + i + '</span>';
    text += ' <span id="x_' + i + '" class="usercheck" onclick="toggleFilter(\'' + i + '\');">';
    if (filtered[i]) {
      text += '&nbsp;&nbsp;';
    } else {
      text += 'x';
    } 
    text += '</span></span> ';
  }
  setHtml('users', text);
}

/*
Toggle filtering out posts for a specific user.  If a user is filtered, the 
posts will be rewritten but without the specified user's posts.

The arguments are:
= user - the user to toggle for filtering.
*/
function toggleFilter(user) {
  if (filtered[user]) {
    filtered[user] = false;
  } else {
    filtered[user] = true;
  }
  loadPostArea();
  toggleUserCheckbox(user, filtered[user]);
}

/*
Toggle the UI representation of a user's filter status - turn it on or off.

The arguments are:
= user - the user to filter.
= isOff - turn the checkbox off if this is true, or on if this is false.
*/
function toggleUserCheckbox(user, isOff) {
  var tag = document.getElementById('x_' + user);
  if (tag) {
    if (isOff) {
      tag.innerHTML = '&nbsp;&nbsp;';
    } else {
      tag.innerHTML = 'x';
    }
  }
}

/*
Sort the page's posts and return them; this is used to ensure the posts are in 
the proper order.
*/
function getSortedPosts() {
  var sortedPosts = new Array();
  for (var key in posts) {
    var p = posts[key];
    var i = sortedPosts.length;
    sortedPosts.push(p);
    while (i > 0 && sortedPosts[i].time < sortedPosts[i - 1].time) {
      swap(sortedPosts, i, i - 1);
      i--;
    }
  }
  return sortedPosts;
}

/*
Load the post area based on JavaScript post objects.  This populates the post
area with HTML span tags representing each of the objects in the page.
*/
function loadPostArea() {
  var sorted = getSortedPosts();
  var text = '';
  for (var i = 0; i < sorted.length; i++) {
    if (!filtered[sorted[i].user.n]) {
      text += convertPostToHtml(sorted[i]);
    }
  }
  setHtml('posts', text);
}

/*
Process new objects for this page.  This is typically loaded via JSON - it
processes user objects and page objects, filling in properties for posts for
ease of access later.

The arguments are:
= pageData - an object with "posts" and "users" attributes that represent data
  from the server.
*/
function handlePageData(pageData) {
  if (pageData) {
    var tempUsers = new Object();
    if (pageData.users) {
      for (var i = 0; i < pageData.users.length; i++) {
        var u = pageData.users[i];
        users[u.n] = u;
        tempUsers[u.i] = u;
      }
      loadUserArea();
    }
    if (pageData.posts) {
      var first = true;
      for (var i = 0; i < pageData.posts.length; i++) {
        var p = pageData.posts[i];
        if (first) {
          first = false;
          lastPost = p.time;
        }
        p.time = parseInt(p.time);
        p.user = tempUsers[p.u];
        p.key = p.time + "__" + p.user.n;
        posts[p.key] = p;
      }
      loadPostArea();
    }
  }
}

/*
This loop is executed every 15 seconds to ensure that there are no additional
posts on the server.  The loop initiates an Ajax request every 15 seconds.
*/
function loadLoop() {
  var msSinceLast = (new Date().getTime() - lastLoad);
  if (msSinceLast > 15000) {
    loadPosts();
    lastLoad = new Date().getTime();
  }
  setTimeout('loadLoop();', 1000);
}
