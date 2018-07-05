$('.checkin-btn').on('click', function() {
  $(this).html("<em class='fa fa-spinner fa-spin'></em> Processing Checkin");
  $(this).tooltip('hide');
  $(this).addClass('disabled')
  $("#grey-out").show()
});
