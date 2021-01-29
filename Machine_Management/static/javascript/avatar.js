(function(w, d){


  function LetterAvatar (name, size) {

      name  = name || '';
      size  = size || 60;
    
var vowels = ["เ", "แ", "โ", "ใ", "ไ"];
var colours = [
              "#A2B01F", "#C6BA59", "#F7CF78", "#F18536", "#D33F33", "#9B89B5", "#E5C3D1", "#B2B7BB", "#5B9BBD", "#5A876F", 
              "#0087BF", "#386894", "#8A75A9", "#D75D5B", "#C85619", "#EC8932", "#AC9B72", "#72ACAE", "#6E8769", "#6A6124"
              ],

    nameSplit = String(name).toUpperCase().split(' '),
        
    initials, charIndex, colourIndex, canvas, context, dataURI;
  
// Check Thai vowel in first name
    if (vowels.includes(nameSplit[0].charAt(0))) {
      first_name = nameSplit[0].charAt(1);
    } else {
      first_name = nameSplit[0].charAt(0);
    }

// Check Thai vowel in last name
    if (nameSplit[1]) {
      if (vowels.includes(nameSplit[1].charAt(0))) {
        last_name = nameSplit[1].charAt(1);
      } else {
        last_name = nameSplit[1].charAt(0);
      }
    }
    
    if (nameSplit.length == 1) {
        initials = first_name;
    } else {
        initials = first_name + last_name;
    }
//      console.log("initials: ",initials);
      

      if (w.devicePixelRatio) {
          size = (size * w.devicePixelRatio);
      }
          
      charIndex     = (initials == '?' ? 72 : initials.charCodeAt(0)) - 64;
      colourIndex   = charIndex % 20;
      canvas        = d.createElement('canvas');
      canvas.width  = size;
      canvas.height = size;
      context       = canvas.getContext("2d");
       
      context.fillStyle = colours[colourIndex - 1];
      context.fillRect (0, 0, canvas.width, canvas.height);
      context.font = Math.round(canvas.width/2.4)+"px sans-serif";
      context.textAlign = "center";
      context.fillStyle = "#FFF";
      context.fillText(initials, size / 2, size / 1.6);

      dataURI = canvas.toDataURL();
      canvas  = null;

      return dataURI;
  }

  LetterAvatar.transform = function() {

      Array.prototype.forEach.call(d.querySelectorAll('img[avatar]'), function(img, name) {
          name = img.getAttribute('avatar');
          img.src = LetterAvatar(name, img.getAttribute('width'));
          img.removeAttribute('avatar');
          img.setAttribute('alt', name);
      });
  };


  // AMD support
  if (typeof define === 'function' && define.amd) {
      
      define(function () { return LetterAvatar; });
  
  // CommonJS and Node.js module support.
  } else if (typeof exports !== 'undefined') {
      
      // Support Node.js specific `module.exports` (which can be a function)
      if (typeof module != 'undefined' && module.exports) {
          exports = module.exports = LetterAvatar;
      }

      // But always support CommonJS module 1.1.1 spec (`exports` cannot be a function)
      exports.LetterAvatar = LetterAvatar;

  } else {
      
      window.LetterAvatar = LetterAvatar;

      d.addEventListener('DOMContentLoaded', function(event) {
          LetterAvatar.transform();
      });
  }

})(window, document);
