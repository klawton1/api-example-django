$(document).ready(function(){
  console.log('connected');
  setTimeout(function(){
    $('.messages').fadeToggle(300);
  },5000);

  $('#walk-in').on('click', function(){
    $('.appointment-choices').hide();
    $('form').show(300);
  })
})