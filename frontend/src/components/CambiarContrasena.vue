<template>
    <div class="change-password-container">
      <h1 class="titulo">Cambiar Contraseña</h1>
      
      <form @submit.prevent="submitForm" class="password-form">
        <div class="form-group">
          <label for="current-password">Contraseña Actual</label>
          <input
            type="password"
            id="current-password"
            v-model="currentPassword"
            required
            placeholder="Ingrese su contraseña actual"
          />
        </div>
  
        <div class="form-group">
          <label for="new-password">Nueva Contraseña</label>
          <input
            type="password"
            id="new-password"
            v-model="newPassword"
            required
            placeholder="Ingrese su nueva contraseña"
          />
        </div>
  
        <div class="form-group">
          <label for="confirm-password">Confirmar Nueva Contraseña</label>
          <input
            type="password"
            id="confirm-password"
            v-model="confirmPassword"
            required
            placeholder="Confirme su nueva contraseña"
          />
        </div>
  
        <div class="form-actions">
          <button type="submit" class="btn btn-submit">Cambiar Contraseña</button>
          <button @click="cancel" class="btn btn-cancel">Cancelar</button>
        </div>
  
        <p v-if="errorMessage" class="error-message">{{ errorMessage }}</p>
      </form>
    </div>
  </template>
  
  <script>
  
  export default {
    data() {
      return {
        currentPassword: "",
        newPassword: "",
        confirmPassword: "",
        errorMessage: "",
      };
    },
    methods: {
      submitForm() {
        if (this.newPassword !== this.confirmPassword) {
          this.errorMessage = "Las contraseñas no coinciden.";
          return;
        }
  
        // Aquí se haría la solicitud al backend para cambiar la contraseña
        const requestData = {
          currentPassword: this.currentPassword,
          newPassword: this.newPassword,
        };
  
        // Realiza la solicitud para cambiar la contraseña
        this.$axios.post('/api/change-password', requestData)
  .then(() => { // No es necesario definir 'response' si no lo usas
    alert('Contraseña cambiada exitosamente.');
    this.$router.push({ name: 'Menu' });
  })
  .catch(() => { // No es necesario definir 'error' si no lo usas
    this.errorMessage = "Error al cambiar la contraseña.";
  });

      },
      cancel() {
        this.$router.push({ name: 'Menu' }); // Redirige al menú principal
      },
    },
  };
  </script>
  
  <style scoped>
  .change-password-container {
    display: flex;
    flex-direction: column;
    align-items: flex-start; /* Alinea el contenido arriba */
    justify-content: flex-start;
    height: auto; /* Ajusta la altura automáticamente */
    width: 100vw; /* Ocupa todo el ancho de la pantalla */
    padding: 20px;
    box-sizing: border-box;
  }
  
  .titulo {
    background-color: #b53b3b;
    color: white;
    padding: 10px;
    width: 100%;
    text-align: center;
  }
  
  .password-form {
    width: 100vw; /* Ocupa todo el ancho de la pantalla */
    background-color: #f9f9f9;
    padding: 40px; /* Espaciado interno */
    border-radius: 8px;
    box-shadow: 0px 4px 12px rgba(0, 0, 0, 0.1);
    margin-top: 20px;
    box-sizing: border-box;
  }
  
  .form-group {
    margin-bottom: 20px;
  }
  
  label {
    display: block;
    margin-bottom: 5px;
    font-weight: bold;
  }
  
  input {
    width: 100%;
    padding: 10px;
    border-radius: 4px;
    border: 1px solid #ccc;
  }
  
  .form-actions {
    display: flex;
    justify-content: space-between;
    margin-top: 20px;
  }
  
  .btn {
    padding: 10px 20px;
    border: none;
    border-radius: 4px;
    cursor: pointer;
  }
  
  .btn-submit {
    background-color: #4CAF50;
    color: white;
  }
  
  .btn-cancel {
    background-color: #b53b3b;
    color: white;
  }
  
  .error-message {
    color: red;
    margin-top: 20px;
    text-align: center;
  }
  </style>
  