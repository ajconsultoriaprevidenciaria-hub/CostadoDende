// Mask: placa Mercosul (AAA0A00)
(function(){
  'use strict';
  function applyMask(input){
    input.addEventListener('input', function(){
      var v = this.value.toUpperCase().replace(/[^A-Z0-9]/g,'');
      if(v.length > 7) v = v.slice(0,7);
      this.value = v;
    });
    input.setAttribute('maxlength','7');
    input.setAttribute('placeholder','AAA0A00');
    input.style.textTransform = 'uppercase';
    input.style.fontFamily = 'monospace';
    input.style.fontWeight = '800';
    input.style.letterSpacing = '.08em';
  }
  function init(){
    var el = document.getElementById('id_placa');
    if(el) applyMask(el);
  }
  if(document.readyState === 'loading'){
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }
})();
