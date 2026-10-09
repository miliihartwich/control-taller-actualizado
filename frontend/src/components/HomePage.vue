<template>
  <div class="home">
    <div class="header">
      <h1>HARTWICH INGENIERIA</h1>
    </div>

    <div class="buttons-container">
      <!-- Usamos router-link para redirigir a las rutas de login y register -->
      <router-link to="/login">
        <button class="btn">Iniciar sesión</button>
      </router-link>
      <router-link to="/register">
        <button class="btn">Registrarse</button>
      </router-link>
    </div>
  </div>
</template>

<script>
export default {
  name: "HomePage",
};
</script>

<style scoped>
/* Estilos generales */
.home {
  text-align: center;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: flex-start; /* Antes estaba en center */
  height: 100vh;
  width: 100vw;
  padding: 20px;
}


.header {
  background-color: rgba(214, 15, 15, 0.8);
  padding: 50px;
  color: white;
  width: 100%;
  text-align: center;
}

h1 {
  margin: 0;
  font-size: 3rem;
}

.buttons-container {
  margin-top: 40px;
  display: flex;
  flex-wrap: wrap;
  justify-content: center;
  gap: 20px;
}

.btn {
  background-color: rgba(214, 15, 15, 0.8);
  color: white;
  font-size: 1.5rem;
  padding: 20px 50px;
  border: none;
  cursor: pointer;
  border-radius: 10px;
  transition: 0.3s;
  width: 250px;
  text-align: center;
}

.btn:hover {
  background-color: rgb(43, 0, 255);
}

/* Estilos responsivos para celulares */
@media (max-width: 768px) {
  .home {
    justify-content: flex-start; /* Alinear todo arriba */
    padding-top: 10px; /* Espacio mínimo arriba */
  }

  .header {
    padding: 10px; /* Reducir espacio alrededor del título */
  }

  h1 {
    font-size: 1.2rem; /* Hacer el título aún más pequeño */
    margin: 0; /* Eliminar márgenes extra */
  }

  .buttons-container {
    flex-direction: column; /* Mantener botones en columna */
    align-items: center; /* Centrar horizontalmente */
    width: 100%;
    margin-top: 20px; /* Separar del título */
    gap: 10px; /* Espacio entre botones */
  }

  .btn {
    width: 100%; /* Botones más largos */
    max-width: 300px; /* Asegurar límite */
    font-size: 0.9rem; /* Reducir el tamaño del texto */
    padding: 12px; /* Ajustar altura */
  }
}


</style>