<template>
    <div class="clientes-container">
      <h1 class="titulo">Lista de Clientes</h1>

      <!-- Barra de Búsqueda -->
      <input
        type="text"
        v-model="filtroNombre"
        placeholder="Buscar por nombre o alias..."
        class="busqueda"
      />

      <!-- Tabla de Clientes -->
      <table class="clientes-tabla">
        <thead>
          <tr>
            <th>RUT/CI</th>
            <th>Nombre</th>
            <th>Alias</th>
            <th>Teléfono</th>
            <th>Whatsapp</th>
            <th>Mail</th>
            <th>Dirección</th>
            <th>Localidad</th>
            <th>Departamento</th>
            <th>Estado</th>
          <th>Acciones</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="cliente in clientesFiltrados" :key="cliente.rut_ci">
            <td>{{ cliente.rut_ci }}</td>
            <td>{{ cliente.nombre }}</td>
            <td>{{ cliente.alias}}</td>
            <td>{{ cliente.telefono }}</td>
            <td>{{ cliente.whatsapp}}</td>
            <td>{{ cliente.mail }}</td>
            <td>{{ cliente.direccion}}</td>
            <td>{{ cliente.localidad_nombre }}</td>
            <td>{{ cliente.departamento_nombre }}</td>
            <td>{{ cliente.estado }}</td>

            <td class="acciones">
              <button @click="toggleEstado(cliente)" class="toggle-btn">
  {{ cliente.estado === 'Activo' ? 'Desactivar' : 'Activar' }}
</button>

          <button @click="editarCliente(cliente)" class="edit-btn">✏️ Editar</button>
        </td>
          </tr>
        </tbody>
      </table>

          <!-- Botón de Menú -->
    <div class="menu-boton-container">
      <button @click="goTo('MenuPage')" class="menu-boton">Menú</button>
    </div>
  </div>

  <div v-if="clienteEditando !== null" class="modal">
    <div class="modal-contenido">
      <h2 class="titulo">Editar Cliente</h2>

      <form @submit.prevent="guardarEdicion" class="formulario">
        <label>Nombre</label>
        <input v-model="clienteEditando.nombre" class="input-field" placeholder="Nombre">

        <label>Alias</label>
        <input v-model="clienteEditando.alias" class="input-field" placeholder="Alias">

        <label>Teléfono</label>
        <input v-model="clienteEditando.telefono" class="input-field" placeholder="Teléfono">

        <label>Whatsapp</label>
        <input v-model="clienteEditando.whatsapp" class="input-field" placeholder="Whatsapp">

        <label>Mail</label>
        <input v-model="clienteEditando.mail" class="input-field" placeholder="Mail">

        <label>Dirección</label>
        <input v-model="clienteEditando.direccion" class="input-field" placeholder="Dirección">

        <label>Departamento</label>
        <select v-model="clienteEditando.departamento_nombre" @change="cargarLocalidades" class="input-field">
          <option v-for="departamento in departamentos" :key="departamento" :value="departamento">
            {{ departamento }}
          </option>
        </select>

        <label>Localidad</label>
        <select v-model="clienteEditando.localidad_nombre">
              <option v-for="localidad in localidades" :key="localidad" :value="localidad">
  {{ localidad}}
</option>
</select>

        <div class="botones">
          <button type="submit" class="btn btn-guardar">Guardar</button>
          <button type="button" @click="clienteEditando = null" class="btn btn-cerrar">Cerrar</button>
        </div>
      </form>
    </div>

    <div v-if="mensaje" class="mensaje">{{ mensaje }}</div>
  </div>
  </template>

<script>
import { apiFetch } from '@/api';

export default {
  data() {
    return {
      clientes: [],
      filtroNombre: "",
      clienteEditando: null,
      mensaje: "",
      departamentos: [],     // lista de nombres de departamentos
      localidades: [],       // lista de nombres de localidades del dpto seleccionado
    };
  },

  computed: {
    clientesFiltrados() {
      const filtro = this.filtroNombre.toLowerCase().trim();
      if (!filtro) return this.clientes;

      return this.clientes
        .map(cliente => {
          const nombre = (cliente.nombre || "").toLowerCase();
          const alias  = (cliente.alias  || "").toLowerCase();

          const comienzaCon = nombre.startsWith(filtro) || alias.startsWith(filtro);
          const contiene    = nombre.includes(filtro)  || alias.includes(filtro);

          return { cliente, prioridad: comienzaCon ? 1 : contiene ? 2 : 3 };
        })
        .filter(item => item.prioridad < 3)
        .sort((a, b) => a.prioridad - b.prioridad)
        .map(item => item.cliente);
    }
  },

  mounted() {
    this.obtenerClientes();
    this.obtenerDepartamentos();
  },

  methods: {
    async obtenerClientes() {
      try {
        const data = await apiFetch('/get_cliente'); // devuelve array
        this.clientes = (Array.isArray(data) ? data : []).map(c => ({
          ...c,
          estado: c.estado || 'Activo'
        }));
      } catch (error) {
        console.error('Error al obtener clientes:', error.message);
      }
    },

    editarCliente(cliente) {
      this.clienteEditando = { ...cliente }; // clona
      this.cargarLocalidades();              // carga localidades del dpto seleccionado
    },

    async guardarEdicion() {
      const password = prompt("Ingrese la contraseña para confirmar:");
      if (password !== "1234") {
        alert("Contraseña incorrecta.");
        return;
      }
      if (!this.clienteEditando) return;

      const c = this.clienteEditando;

      // el backend espera estos nombres de campos:
      const body = {
        nombre: c.nombre,
        alias: c.alias,
        telefono: c.telefono,
        whatsapp: c.whatsapp,
        mail: c.mail,
        direccion: c.direccion,
        departamento_nombre: c.departamento_nombre,
        localidad_nombre: c.localidad_nombre,
        estado: c.estado   // "Activo" | "Inactivo"
      };

      try {
        await apiFetch(`/update_cliente/${encodeURIComponent(c.rut_ci)}`, {
          method: 'PUT',
          body
        });

        alert("Cliente editado correctamente");
        await this.obtenerClientes();  // refresca
        this.clienteEditando = null;   // cierra modal
      } catch (error) {
        alert("Error al editar: " + (error.message || 'desconocido'));
      }
    },

    async toggleEstado(cliente) {
      const confirmacion = prompt("Ingrese la contraseña para confirmar:");
      if (confirmacion !== "1234") {
        alert("Contraseña incorrecta");
        return;
      }

      const nuevoEstado = cliente.estado === "Activo" ? "Inactivo" : "Activo";

      const body = {
        nombre: cliente.nombre,
        alias: cliente.alias,
        telefono: cliente.telefono,
        whatsapp: cliente.whatsapp,
        mail: cliente.mail,
        direccion: cliente.direccion,
        departamento_nombre: cliente.departamento_nombre,
        localidad_nombre: cliente.localidad_nombre,
        estado: nuevoEstado
      };

      try {
        await apiFetch(`/update_cliente/${encodeURIComponent(cliente.rut_ci)}`, {
          method: 'PUT',
          body
        });

        // actualiza en memoria sin recargar todo
        const i = this.clientes.findIndex(c => c.rut_ci === cliente.rut_ci);
        if (i !== -1) {
          this.clientes[i] = { ...this.clientes[i], estado: nuevoEstado };
          this.clientes = [...this.clientes]; // fuerza re-render
        }
      } catch (error) {
        alert("Error al actualizar estado: " + (error.message || 'desconocido'));
      }
    },

    async obtenerDepartamentos() {
      try {
        const data = await apiFetch('/departamentos'); // { departamentos: [...] }
        this.departamentos = Array.isArray(data?.departamentos) ? data.departamentos : [];
      } catch (error) {
        console.error('Error al obtener departamentos:', error.message);
      }
    },

    async cargarLocalidades() {
      if (!this.clienteEditando || !this.clienteEditando.departamento_nombre) return;
      try {
        const data = await apiFetch(`/localidades?departamento=${encodeURIComponent(this.clienteEditando.departamento_nombre)}`);
        this.localidades = Array.isArray(data?.localidades) ? data.localidades : [];

        // si la localidad actual ya no pertenece al dpto, limpiarla
        if (!this.localidades.includes(this.clienteEditando.localidad_nombre)) {
          this.clienteEditando.localidad_nombre = "";
        }
      } catch (error) {
        console.error('Error al obtener localidades:', error.message);
      }
    },

    goTo(routeName) {
      this.$router.push({ name: routeName });
    },
  },

  watch: {
    // cuando cambie el departamento en el modal, recargar localidades
    'clienteEditando.departamento_nombre'(nuevo) {
      if (nuevo) this.cargarLocalidades();
      else this.localidades = [];
    }
  }
};
</script>

<style scoped>
  /* Contenedor principal */
  .clientes-container {
    width: 90%;
    max-width: 1200px;
    margin: 20px auto;
    text-align: center;
  }

  /* Estilos del título */
  .titulo {
    background-color: #b53b3b;
    color: white;
    padding: 10px;
    font-weight: bold;
    font-size: 1.5rem;
    text-align: center;
    margin-bottom: 15px;
  }

  /* Input de búsqueda */
  .busqueda {
    width: 100%;
    padding: 8px;
    margin: 10px 0;
    border: 1px solid #ccc;
    border-radius: 5px;
    font-size: 1rem;
  }

  /* Estilos de la tabla */
  .clientes-tabla {
    width: 100%;
    border-collapse: collapse;
    margin-top: 10px;
    font-size: 12px;
  }


  .clientes-tabla th, .clientes-tabla td {
    border: 1px solid #aa3434;
    padding: 8px;
    text-align: left;
    font-size: 12px;
    border: 1px solid black;
  }

/* Estilo de los títulos de la tabla - MISMO COLOR QUE EL TÍTULO */
.clientes-tabla thead {
  background-color: #b53b3b; /* Mismo color que el título */
  color: white;
}

/* Filas alargadas y finas */
.clientes-tabla td {
  padding: 12px 8px; /* Ajusta la altura */
}


  .menu-boton-container {
  display: flex;
  justify-content: center;
  align-items: center;
  padding: 10px;
}

.menu-boton {
  background-color: #992f2f;
  color: white;
  border: none;
  padding: 10px 20px;
  font-size: 16px;
  cursor: pointer;
  border-radius: 5px;
}


  .menu-boton:hover {
    background-color: #992f2f;
  }

  /* Estilos del modal */
  .modal-overlay {
    position: fixed;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    background: rgba(0, 0, 0, 0.5);
    display: flex;
    justify-content: center;
    align-items: center;
  }

  .modal {
  position: fixed; /* Fija el modal en la pantalla */
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: rgba(0, 0, 0, 0.5); /* Fondo semitransparente */
  display: flex;
  justify-content: center;
  align-items: center; /* Centra el modal */
  z-index: 1000; /* Asegura que esté encima del contenido */
}

.modal-contenido {
  background: white;
  padding: 20px;
  border-radius: 8px;
  width: 90%;
  max-width: 400px;
  box-shadow: 0 4px 10px rgba(0, 0, 0, 0.3);
  text-align: center;
  position: relative;
}


  /* Estilos del formulario */
  .formulario {
    display: flex;
    flex-direction: column;
    gap: 10px;
  }

  .input-field {
    width: 100%;
    padding: 8px;
    border: 1px solid #ccc;
    border-radius: 4px;
    font-size: 1rem;
  }

  /* Estilos de los botones */
  .botones {
    display: flex;
    justify-content: space-between;
    margin-top: 15px;
  }

  .btn {
    padding: 10px 15px;
    border: none;
    border-radius: 5px;
    cursor: pointer;
    font-size: 1rem;
    transition: background 0.3s;
  }

  .btn-guardar {
    background: #28a745;
    color: white;
  }

  .btn-guardar:hover {
    background: #218838;
  }

  .btn-cerrar {
    background: #dc3545;
    color: white;
  }

  .btn-cerrar:hover {
    background: #c82333;
  }

  /* Mensaje de confirmación */
  .mensaje {
    margin-top: 10px;
    padding: 10px;
    background: lightgreen;
    text-align: center;
    border-radius: 5px;
  }

  /* Ajustes en los botones generales */
  button {
    margin: 5px;
    padding: 5px 10px;
    border: none;
    border-radius: 5px;
    cursor: pointer;
  }
  table {
  width: 100%;
  border-collapse: collapse;
}

th, td {
  border: 1px solid black; /* Línea de separación */
  padding: 8px;
  text-align: left;
}

/* Eliminar este estilo que está sobrescribiendo el color de los encabezados */
/* th {
  background-color: #f2f2f2;
} */

/* Asegurar que los encabezados de la tabla tengan el color correcto */
.clientes-tabla th {
  background-color: #b53b3b;
  color: white;
}
</style>