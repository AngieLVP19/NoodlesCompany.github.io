function validar_formulario() {
    var email = document.formLogin.correo;
    var password = document.formLogin.contraseña;
  
    var formato_email = /^\w+([\.-]?\w+)@\w+([\.-]?\w+)(\.\w{2,3})+$/;
    if (!email.value.match(formato_email)) {
      alert("Debes ingresar un email electrónico valido!");
      return false; //Para que los datos se conserven
      
    }
  
    var passid_len = password.value.length;
    if (passid_len == 0 || passid_len < 8) {
      alert("Debes ingresar una password con mas de 8 caracteres");
      return false; //Para que los datos se conserven
    }
  }

  function mostrarPassword(){
    var objeto=document.getElementById("correo")
    objeto.type="text"
  }
  function ocultarPassword(){
    var objeto=document.getElementById("contraseña")
    objeto.type="password"
  }