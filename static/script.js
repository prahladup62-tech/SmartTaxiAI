document.addEventListener('DOMContentLoaded', function(){
  var r = document.getElementById('registerForm');
  if(r){
    r.addEventListener('submit', function(e){
      var pwd = r.querySelector('input[name="password"]').value;
      if(pwd.length < 4){
        e.preventDefault();
        alert('Password should be at least 4 characters');
      }
    });
  }
});
