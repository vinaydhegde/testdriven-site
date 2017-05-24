$(function() {

  var $obj = $('#toc-block');
  var $top = $obj.offset().top;

  setSideBarDisplay($obj, $top);

  $(window).scroll(function (event) {
    setSideBarDisplay($obj, $top);
  });

  var active = window.location.href.split('-')[1];
  if (active) {
    if (active === 'one') {
      $('h5[data-part="1"]').addClass('active');
    }
    if (active === 'two') {
      $('h5[data-part="2"]').addClass('active');
    }
  }

});

// helpers

function setSideBarDisplay(obj, top) {
  var y = $(window).scrollTop();
  if (y >= top - 51) {
    obj.css('position', 'fixed').css('top', '45px');
  } else {
    obj.css('position', 'static').css('top', '0px');
  }
}
