$(document).ready(function(){
  console.log('connected');
  setTimeout(function(){
    $('.messages').fadeToggle(300);
  },5000);

  $('#walk-in').on('click', function(){
    $('.appointment-choices').hide();
    $('form').show(300);
  });

  $('.see-patient').click(function(e){
    e.preventDefault();
    if (confirm(`Ready to see this patient?`)){
      $(this).closest('form.appointment-form').submit();
    }
  });

  $('.select-status').on('change', function(){
    if (confirm(`Update this appointment to ${this.value}?`)){
      $(this).closest('form.appointment-form').submit();
    }else{
      $(this).val($(this).children().first().val());
    }
  });
})