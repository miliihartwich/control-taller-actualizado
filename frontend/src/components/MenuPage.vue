<template>
  <div class="page-root">
    <div class="menu-container">
      <h1 class="titulo">MENÚ</h1>

      <div class="grid grid-cols-4 gap-8">
        <!-- Columna de Formularios de Registro -->
        <div class="column">
          <h2 class="column-title formularios-registro">Formularios de Registro</h2>
          <button @click="goTo('ClienteForm')" class="btn btn-register">Registrar Cliente</button>
          <button @click="goTo('ProveedorForm')" class="btn btn-register">Registrar Proveedor</button>
          <button @click="goTo('EmpleadoForm')" class="btn btn-register">Registrar Empleado</button>
          <button @click="goTo('IntervencionForm')" class="btn btn-register">Registrar Intervención</button>
          <button @click="goTo('OrdenesForm')" class="btn btn-register">Registrar Nueva Orden</button>
          <button @click="goTo('ComprasForm')" class="btn btn-register">Ingresar Compra de bienes</button>
          <button @click="goTo('ServiciosForm')" class="btn btn-register">Ingresar Compra de servicios</button>
        </div>

        <!-- Columna de Listados -->
        <div class="column">
          <h2 class="column-title listados">Listados y Edición</h2>
          <button @click="goTo('VerClientes')" class="btn btn-list">Ver Clientes</button>
          <button @click="goTo('VerProveedores')" class="btn btn-list">Ver Proveedores</button>
          <button @click="goTo('VerEmpleados')" class="btn btn-list">Ver Empleados</button>
          <button @click="goTo('VerOrdenes')" class="btn btn-list">Ver Ordenes</button>
          <button @click="goTo('VerStock')" class="btn btn-list">Ver Stock</button>
          <button @click="goTo('VerServicios')" class="btn btn-list">Ver Compras Servicios</button>
          <button @click="goTo('VerClasificacionOrdenes')" class="btn btn-list">Ver Clasificacion Ordenes</button>
          <button @click="goTo('IntervencionesTodas')" class="btn btn-list">Todas las intervenciones</button>
        </div>

        <!-- Columna de Consultas -->
        <div class="column">
          <h2 class="column-title consultas">Consultas</h2>
          <button @click="goTo('ConsultaIntervenciones')" class="btn btn-consult">Intervenciones por empleado</button>
          <button @click="goTo('ConsultaCostosPorOrden')" class="btn btn-consult">Costos por orden</button>
        </div>

        <!-- Columna de Configuraciones -->
        <div class="column">
          <h2 class="column-title configuraciones">Configuraciones 🔒</h2>
          <button @click.stop="openModal('ClasificacionOrdenes')" class="btn btn-config">Clasificación de Órdenes</button>
          <button @click.stop="openModal('ConfiguracionesForm')" class="btn btn-config">Parámetros</button>
          <button v-if="esPropietario" @click.stop="openModal('EditarRoles')" class="btn btn-config">
            Editar Roles
          </button>
        </div>
      </div>

      <div class="mt-8 flex justify-center space-x-4">
        <button class="btn btn-secondary" @click="logout">Cerrar sesión</button>
      </div>
    </div>

    <!-- Modal de contraseña -->
    <div v-if="showModal" class="modal-overlay" @click="closeModal">
      <div class="modal" @click.stop>
        <h2>Ingrese la contraseña para acceder</h2>
        <input
          type="password"
          v-model="passwordInput"
          placeholder="Contraseña"
          class="password-input"
        />
        <p v-if="errorMessage" class="error-message">{{ errorMessage }}</p>
        <div class="modal-actions">
          <button class="btn btn-submit" @click="verifyPassword">Aceptar</button>
          <button class="btn btn-cancel" @click="closeModal">Cancelar</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  data() {
    return {
      showModal: false,
      passwordInput: "",
      errorMessage: "",
      requestedRoute: null,
      rolUsuario: "", // Guarda el rol del usuario logueado
    };
  },
  computed: {
    // Devuelve true si el usuario es propietario
    esPropietario() {
      return this.rolUsuario === "propietario";
    },
  },
  methods: {
    openModal(route) {
      console.log("Abriendo modal para:", route);
      this.requestedRoute = route;
      this.showModal = true;
      this.passwordInput = "";
      this.errorMessage = "";
    },
    closeModal() {
      console.log("Cerrando modal");
      this.showModal = false;
      this.requestedRoute = null;
    },
    verifyPassword() {
      const correctPassword = "1234";
      if (this.passwordInput === correctPassword) {
        console.log("Contraseña correcta. Redirigiendo a:", this.requestedRoute);
        this.$router.push({ name: this.requestedRoute });
        this.closeModal();
      } else {
        console.log("Contraseña incorrecta");
        this.errorMessage = "Contraseña incorrecta.";
      }
    },
    goTo(routeName) {
      this.$router.push({ name: routeName });
    },
logout() {
  if (!confirm("¿Está seguro de que desea cerrar sesión?")) return;

  // 1) limpiar TODA la sesión DEV
  localStorage.removeItem("usuario");
  localStorage.removeItem("rol");
  localStorage.removeItem("cedula");

  // 2) limpiar restos legacy por si quedaron
  localStorage.removeItem("token");
  localStorage.removeItem("access_token");
  localStorage.removeItem("jwt");
  sessionStorage.removeItem("token");
  sessionStorage.removeItem("access_token");
  sessionStorage.removeItem("jwt");

  // 3) (opcional pero recomendado) limpiar todo localStorage si no guardás nada más crítico
  // localStorage.clear();

  // 4) navegación “dura” para evitar que el guard te re-dirija por estado raro
  window.location.href = "/login";
}
  },

  mounted() {
    // Obtener el rol del usuario desde localStorage
    this.rolUsuario = localStorage.getItem("rol") || "";
   
  },
};
</script>

  <style scoped>
  .menu-container {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    min-height: 100vh;
  }
  
  .grid {
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 2rem;
    width: 100%;
  }
  
  .column {
    display: flex;
    flex-direction: column;
    align-items: center;
  }
  
  .column-title {
  margin-top: 30px; /* Espacio superior entre el título del menú y las columnas */
  margin-bottom: 1rem;
  padding: 10px 20px;
  border-radius: 0; /* Esquinas rectas */
  font-size: 1.5rem;
  text-align: center;
  width: 90%;
}

  
  .btn {
    padding: 15px 30px;
    width: 100%;
    margin-bottom: 1rem;
    border-radius: 8px;
    font-size: 1.2rem;
    cursor: pointer;
    transition: background-color 0.3s;
  }
  
  .btn-register {
  background-color: #2f1ecb93;; /* Morado claro para botones de registros */
  color: white;
}

.btn-list {
  background-color: rgba(242, 172, 43, 0.7); /* Naranja claro para botones de listados */
  color: white;
}

.btn-consult {
  background-color: rgba(104, 196, 74, 0.7); /* Verde claro para botones de consultas */
  color: white;
}

.btn-config {
  background-color: rgba(114, 118, 121, 0.7); /* Gris claro para botones de configuraciones */
  color: white;
}
  
  .btn-secondary {
    background-color: #b53b3b; /* Rojo oscuro para opciones secundarias */
    color: white;
    padding: 10px 20px;
  }
  
  .formularios-registro {
    background-color: #2f1ecbc4; /* Morado para sección de formularios */
  }
  
  .listados {
    background-color: #FFA500; /* Naranja para sección de listados */
  }
  
  .consultas {
    background-color: rgba(105, 196, 74, 0.934);  /* Verde para sección de consultas */
  }
  
  .configuraciones {
    background-color: #6c757d; /* Gris para sección de configuraciones */
  }
  
  .mt-8 {
    margin-top: 2rem;
  }
  
  .ml-4 {
    margin-left: 1rem;
  }
  .titulo {
  background-color: #b53b3b;
  color: white;
  padding: 20px; /* Aumenta el padding para darle más espacio */
  text-align: center;
  border-radius: 4px;
  width: 100vw; /* Abarca todo el ancho de la ventana */
  margin: 0; /* Elimina margen externo */
  position: fixed; /* Hace que el título esté fijo en la parte superior */
  top: 0; /* Lo coloca al inicio de la pantalla */
  left: 0; /* Alineado al borde izquierdo */
  z-index: 1; /* Asegura que esté sobre otros elementos */
}
/* Estilos del modal */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100vw;
  height: 100vh;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
}

.modal {
  background: white;
  padding: 20px;
  border-radius: 8px;
  text-align: center;
  width: 300px;
  box-shadow: 0px 4px 12px rgba(0, 0, 0, 0.3);
}

.password-input {
  width: 100%;
  padding: 10px;
  margin: 10px 0;
  border: 1px solid #ccc;
  border-radius: 4px;
}

.modal-actions {
  display: flex;
  justify-content: space-between;
}

.btn-submit {
  background-color: #4CAF50;
  color: white;
  padding: 10px 20px;
  border: none;
  cursor: pointer;
}

.btn-cancel {
  background-color: #b53b3b;
  color: white;
  padding: 10px 20px;
  border: none;
  cursor: pointer;
}

.error-message {
  color: red;
  font-size: 0.9rem;
}

  </style>
  