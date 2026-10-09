<template>
  <div class="proveedores-container">
    <h1 class="titulo">Lista de Proveedores</h1>
    
    <!-- Barra de Búsqueda -->
    <input 
      type="text" 
      v-model="filtroNombre" 
      placeholder="Buscar por nombre o rubro..." 
      class="busqueda"
    />
    
    <!-- Tabla de Proveedoress -->
    <table class="proveedores-tabla">
      <thead>
        <tr>
          <th>RUT/CI</th>
          <th>Nombre</th>
          <th>Alias</th>
          <th>Teléfono</th>
          <th>Whatsapp</th>
          <th>Mail</th>
          <th>Rubro</th>
          <th>Dirección</th>
          <th>Localidad</th>
          <th>Departamento</th>
          <th>Calificacion</th>
          <th>Comentarios</th>
          <th>Estado</th>
          <th>Acciones</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="proveedor in proveedoresFiltrados" :key="proveedor.rut_ci">
          <td>{{ proveedor.rut_ci }}</td>
          <td>{{ proveedor.nombre }}</td>
          <td>{{ proveedor.alias}}</td>
          <td>{{ proveedor.telefono }}</td>
          <td>{{ proveedor.whatsapp}}</td>
          <td>{{ proveedor.mail }}</td>
          <td>{{ proveedor.rubro }}</td>
          <td>{{ proveedor.direccion}}</td>
          <td>{{ proveedor.localidad_nombre }}</td>
          <td>{{ proveedor.departamento_nombre }}</td>  
          <td>{{ proveedor.calificacion }}</td> 
          <td>{{ proveedor.comentarios }}</td>
          <td>{{ proveedor.estado }}</td>


          <td class="acciones">
              <button @click="toggleEstado(proveedor)" class="toggle-btn">
  {{ proveedor.estado === 'Activo' ? 'Desactivar' : 'Activar' }}
</button>
          <button @click="editarProveedor(proveedor)" class="edit-btn">✏️ Editar</button>
        </td>
      </tr>
    </tbody>
  </table>
</div>

    <!-- Botón de Menú -->
    <div class="menu-boton-container">
      <button @click="goTo('MenuPage')" class="menu-boton">Menú</button>
    </div>
 
    
<div v-if="proveedorEditando !== null" class="modal">
    <div class="modal-contenido">
      <h2 class="titulo">Editar Proveedor</h2>

      <form @submit.prevent="guardarEdicion" class="formulario">
        <label>Nombre</label>
        <input v-model="proveedorEditando.nombre" class="input-field" placeholder="Nombre">

        <label>Alias</label>
        <input v-model="proveedorEditando.alias" class="input-field" placeholder="Alias">

        <label>Teléfono</label>
        <input v-model="proveedorEditando.telefono" class="input-field" placeholder="Teléfono">

        <label>Whatsapp</label>
        <input v-model="proveedorEditando.whatsapp" class="input-field" placeholder="Whatsapp">

        <label>Mail</label>
        <input v-model="proveedorEditando.mail" class="input-field" placeholder="Mail">

        <label>Rubro</label>
        <select v-model="proveedorEditando.rubro" class="input-field">
          <option v-for="rubro in rubros" :key="rubro.id" :value="rubro.nombre">
            {{ rubro.nombre }}
          </option>
        </select>

        <label>Dirección</label>
        <input v-model="proveedorEditando.direccion" class="input-field" placeholder="Dirección">

        <label>Departamento</label>
        <select v-model="proveedorEditando.departamento_nombre" @change="cargarLocalidades" class="input-field">
          <option v-for="departamento in departamentos" :key="departamento" :value="departamento">
            {{ departamento }}
          </option>
        </select>

        <label>Localidad</label>
        <select v-model="proveedorEditando.localidad_nombre">
          <option v-for="localidad in localidades" :key="localidad" :value="localidad">
  {{ localidad }}
</option>

</select>

        <label>Calificación</label>
        <input v-model="proveedorEditando.calificacion" class="input-field" type="number" min="1" max="10" placeholder="Calificación">

        <label>Comentarios</label>
        <textarea v-model="proveedorEditando.comentarios" class="input-field" placeholder="Comentarios"></textarea>

        <div class="botones">
          <button type="submit" class="btn btn-guardar">Guardar</button>
          <button type="button" @click="proveedorEditando = null" class="btn btn-cerrar">Cerrar</button>
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
      proveedores: [],
      filtroNombre: "",
      proveedorEditando: null,
      mensaje: "",
      departamentos: [],   // nombres de departamentos
      localidades: [],     // localidades del depto seleccionado
      rubros: []           // [{id, nombre}]
    };
  },

  computed: {
    proveedoresFiltrados() {
      const filtro = this.filtroNombre.toLowerCase().trim();
      if (!filtro) return this.proveedores;

      return this.proveedores
        .map(proveedor => {
          const nombre = (proveedor.nombre || "").toLowerCase();
          const rubro  = (proveedor.rubro  || "").toLowerCase();
          const comienzaCon = nombre.startsWith(filtro) || rubro.startsWith(filtro);
          const contiene    = nombre.includes(filtro)   || rubro.includes(filtro);
          return { proveedor, prioridad: comienzaCon ? 1 : contiene ? 2 : 3 };
        })
        .filter(i => i.prioridad < 3)
        .sort((a, b) => a.prioridad - b.prioridad)
        .map(i => i.proveedor);
    }
  },

  mounted() {
    this.obtenerProveedores();
    this.obtenerDepartamentos();
    this.obtenerRubros();
  },

  methods: {
    async obtenerProveedores() {
      try {
        const data = await apiFetch('/get_proveedor'); // array de objetos
        this.proveedores = Array.isArray(data) ? data : [];
      } catch (error) {
        console.error("Error al obtener proveedores:", error.message);
      }
    },

    editarProveedor(proveedor) {
      // Los campos vienen como *_nombre desde el backend (ver /get_proveedor)
      this.proveedorEditando = { ...proveedor };
      this.cargarLocalidades(); // usa proveedorEditando.departamento_nombre
    },

    async guardarEdicion() {
      const password = prompt("Ingrese la contraseña para confirmar:");
      if (password !== "1234") {
        alert("Contraseña incorrecta.");
        return;
      }

      const p = this.proveedorEditando || {};
      // Payload que tu endpoint /update_proveedor espera (por nombres)
      const payload = {
        nombre: p.nombre,
        alias: p.alias,
        telefono: p.telefono,
        whatsapp: p.whatsapp,
        mail: p.mail,
        rubro: p.rubro, // nombre del rubro
        direccion: p.direccion,
        localidad_nombre: p.localidad_nombre || p.localidad || "",     // por si viene con otra clave
        departamento_nombre: p.departamento_nombre || p.departamento || "",
        calificacion: p.calificacion,
        comentarios: p.comentarios,
        estado: p.estado
      };

      try {
        await apiFetch(`/update_proveedor/${encodeURIComponent(p.rut_ci)}`, {
          method: 'PUT',
          body: payload
        });
        alert("Proveedor editado correctamente");
        await this.obtenerProveedores();
        this.proveedorEditando = null;
      } catch (error) {
        alert("Error al editar: " + (error.message || "desconocido"));
      }
    },

    async toggleEstado(proveedor) {
      const confirmacion = prompt("Ingrese la contraseña para confirmar:");
      if (confirmacion !== "1234") {
        alert("Contraseña incorrecta");
        return;
      }

      const nuevoEstado = proveedor.estado === "Activo" ? "Inactivo" : "Activo";
      const base = { ...proveedor, estado: nuevoEstado };

      const payload = {
        nombre: base.nombre,
        alias: base.alias,
        telefono: base.telefono,
        whatsapp: base.whatsapp,
        mail: base.mail,
        rubro: base.rubro,
        direccion: base.direccion,
        localidad_nombre: base.localidad_nombre || base.localidad || "",
        departamento_nombre: base.departamento_nombre || base.departamento || "",
        calificacion: base.calificacion,
        comentarios: base.comentarios,
        estado: base.estado
      };

      try {
        await apiFetch(`/update_proveedor/${encodeURIComponent(base.rut_ci)}`, {
          method: 'PUT',
          body: payload
        });

        // Actualizar localmente sin recargar todo
        const idx = this.proveedores.findIndex(c => c.rut_ci === base.rut_ci);
        if (idx !== -1) {
          this.proveedores[idx] = { ...this.proveedores[idx], estado: nuevoEstado };
          this.proveedores = [...this.proveedores];
        }
      } catch (error) {
        alert("Error al actualizar estado: " + (error.message || "desconocido"));
      }
    },

    async obtenerDepartamentos() {
      try {
        const data = await apiFetch('/departamentos'); // { departamentos: [...] }
        this.departamentos = data?.departamentos || [];
      } catch (error) {
        console.error("Error al obtener departamentos:", error.message);
      }
    },

    async cargarLocalidades() {
      const depto = this.proveedorEditando?.departamento_nombre;
      if (!depto) return;

      try {
        const data = await apiFetch(`/localidades?departamento=${encodeURIComponent(depto)}`); // {localidades:[...]}
        this.localidades = data?.localidades || [];

        // Normalizar la clave de localidad en el objeto editado
        const locActual = this.proveedorEditando.localidad_nombre || this.proveedorEditando.localidad || "";
        if (!this.localidades.includes(locActual)) {
          // si no está, vaciamos para forzar selección válida
          this.proveedorEditando.localidad_nombre = "";
        } else {
          // asegurar que usamos localidad_nombre
          this.proveedorEditando.localidad_nombre = locActual;
        }
      } catch (error) {
        console.error("Error al obtener localidades:", error.message);
      }
    },

    async obtenerRubros() {
      try {
        const data = await apiFetch('/rubros'); // { rubros: [{id, nombre}] }
        this.rubros = data?.rubros || [];
      } catch (error) {
        console.error("Error al obtener rubros:", error.message);
      }
    },

    goTo(routeName) {
      this.$router.push({ name: routeName });
    }
  }
};
</script>

  
  
  <style scoped>
  /* Contenedor principal */
  .proveedores-container {
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
  .proveedores-tabla {
    width: 100%;
    border-collapse: collapse;
    margin-top: 10px;
    font-size: 12px;
  }
  
  .proveedores-tabla thead {
    background-color: #b53b3b;
    color: white;
  }
  
  .proveedores-tabla th, .proveedores-tabla td {
    border: 1px solid #ccc;
    padding: 8px;
    text-align: left;
    font-size: 12px;
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
  </style>
  