$(function() {

  var $obj = $('#toc-block');
  var $top = $obj.offset().top;

  $(window).scroll(function (event) {
    var y = $(this).scrollTop();
    if (y >= $top - 51) {
      $obj.css('position', 'fixed').css('top', '45px');
    } else {
      $obj.css('position', 'static').css('top', '0px');
    }
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
