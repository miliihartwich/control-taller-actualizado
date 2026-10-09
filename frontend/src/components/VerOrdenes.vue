<template>
  <div class="ordenes-container">
    <h1 class="titulo">Lista de Órdenes</h1>
    
    <input 
      type="text" 
      v-model="filtro" 
      placeholder="Buscar por cliente,división,tipo o desripción..." 
      class="busqueda"
    />
    
    <table class="ordenes-tabla">
      <thead>
        <tr>
          <th>ID</th>
          <th>División</th>
          <th>Tipo</th>
          <th>Descripción</th>
          <th>Cliente</th>
          <th>Fecha Inicio</th>
          <th>Fecha Fin</th>
          <th>Estado</th>
          <th>Acciones</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="orden in ordenesFiltradas" :key="orden.numero_orden">
          <td>{{ orden.numero_orden }}</td>
          <td>{{ orden.division }}</td>
          <td>{{ orden.tipo }}</td>
          <td>{{ orden.descripcion }}</td>
          <td>{{ orden.cliente }}</td>
          <td>{{ formatFecha(orden.fecha_inicio) }}</td>
          <td>{{ orden.fecha_fin ? formatFecha(orden.fecha_fin) : '-' }}</td>
          <td>{{ orden.estado }}</td>
          <td>
            <button @click="editarOrden(orden)" class="edit-btn">✏️ Editar</button>
            <button @click="abrirModalEstado(orden)" class="estado-btn">Desactivar</button>
          </td>
        </tr>
      </tbody>
    </table>
  </div>

  <!-- Botón de Menú -->
  <div class="menu-boton-container">
    <button @click="goTo('MenuPage')" class="menu-boton">Menú</button>
  </div>

  <div v-if="ordenEditando" class="modal">
    <div class="modal-contenido">
      <h2 class="titulo">Editar Orden</h2>
      <form @submit.prevent="guardarEdicion" class="formulario">
        <label>División</label>
        <select v-model="ordenEditando.division" class="input-field">
          <option v-for="division in divisiones" :key="division" :value="division">
            {{ division }}
          </option>
        </select>

        <label>Tipo</label>
        <select v-model="ordenEditando.tipo" class="input-field">
          <option v-for="tipo in tipos" :key="tipo" :value="tipo">
            {{ tipo }}
          </option>
        </select>

        <label>Descripción</label>
        <input v-model="ordenEditando.descripcion" class="input-field" placeholder="Descripción">

        <label>Cliente</label>
        <select v-model="ordenEditando.cliente" class="input-field">
          <option v-for="cliente in clientes" :key="cliente.rut_ci" :value="cliente.nombre">
            {{ cliente.nombre }}
          </option>
        </select>

        <label>Fecha Inicio</label>
        <input type="date" v-model="ordenEditando.fecha_inicio" class="input-field">

        <label>Fecha Fin</label>
        <input type="date" v-model="ordenEditando.fecha_fin" class="input-field">

        <div class="botones">
          <button type="submit" class="btn btn-guardar">Guardar</button>
          <button type="button" @click="ordenEditando = null" class="btn btn-cerrar">Cerrar</button>
        </div>
      </form>
    </div>
  </div>

  <div v-if="ordenEstadoEditando" class="modal">
    <div class="modal-contenido">
      <h2 class="titulo">Desactivar</h2>
      <form @submit.prevent="guardarEstado">
        <label>Estado</label>
        <select v-model="ordenEstadoEditando.estado" class="input-field">
          <option value="Activa">Activa</option>
          <option value="En pausa">En pausa</option>
          <option value="Finalizada">Finalizada</option>
        </select>
        <div class="botones">
          <button type="submit" class="btn btn-guardar">Guardar</button>
          <button type="button" @click="ordenEstadoEditando = null" class="btn btn-cerrar">Cerrar</button>
        </div>
      </form>
    </div>
  </div>
</template>


<script>
import { apiFetch } from '@/api';

export default {
  data() {
    return {
      ordenes: [],
      filtro: "",
      ordenEditando: null,
      ordenEstadoEditando: null,
      divisiones: [],
      tipos: [],
      clientes: []
    };
  },

  computed: {
    ordenesFiltradas() {
      const filtro = this.filtro.toLowerCase().trim();
      if (!filtro) return this.ordenes;
      return this.ordenes.filter(o =>
        (o.cliente || "").toLowerCase().includes(filtro) ||
        (o.division || "").toLowerCase().includes(filtro) ||
        (o.tipo || "").toLowerCase().includes(filtro) ||
        (o.descripcion || "").toLowerCase().includes(filtro)
      );
    }
  },

  watch: {
    ordenEditando: {
      handler(nuevaOrden) {
        if (nuevaOrden && nuevaOrden.division) {
          this.obtenerTipos(nuevaOrden.division);
        }
      },
      deep: true
    }
  },

  mounted() {
    this.obtenerOrdenes();
    this.obtenerDivisiones();
    this.obtenerClientes();
    // this.obtenerTipos(); // <- ya no llamamos sin división
  },

  methods: {
    // Helpers
    formatFecha(fecha) {
      return fecha ? new Date(fecha).toISOString().split('T')[0] : "";
    },
    buildUpdatePayload(src) {
      return {
        division: src.division,
        tipo: src.tipo,
        descripcion: src.descripcion,
        cliente: src.cliente,               // tu backend usa 'cliente' en update
        fecha_inicio: src.fecha_inicio || null,
        fecha_fin: src.fecha_fin || null,
        estado: src.estado || 'Activa'
      };
    },

    // Cargas
    async obtenerOrdenes() {
      try {
        const data = await apiFetch('/ordenes_listado');
        this.ordenes = Array.isArray(data) ? data : [];
      } catch (error) {
        console.error("Error al obtener órdenes:", error.message);
      }
    },

    async obtenerDivisiones() {
      try {
        const data = await apiFetch('/divisiones'); // array de strings
        this.divisiones = Array.isArray(data) ? data : (data?.divisiones || []);
      } catch (error) {
        console.error("Error al obtener divisiones:", error.message);
      }
    },

    async obtenerTipos(nombreDivision) {
      if (!nombreDivision) return;
      try {
        const data = await apiFetch(`/tipos_por_division/${encodeURIComponent(nombreDivision)}`);
        this.tipos = Array.isArray(data) ? data : (data?.tipos || []);
      } catch (error) {
        console.error("Error al obtener tipos:", error.message);
      }
    },

    async obtenerClientes() {
      try {
        const data = await apiFetch('/clientes'); // [{rut_ci,nombre}]
        this.clientes = Array.isArray(data) ? data : [];
      } catch (error) {
        console.error("Error al obtener clientes:", error.message);
      }
    },

    // Edición completa
    editarOrden(orden) {
      this.ordenEditando = {
        ...orden,
        fecha_inicio: this.formatFecha(orden.fecha_inicio),
        fecha_fin: orden.fecha_fin ? this.formatFecha(orden.fecha_fin) : ""
      };
    },

    async guardarEdicion() {
      try {
        const payload = this.buildUpdatePayload(this.ordenEditando);
        await apiFetch(`/update_orden/${encodeURIComponent(this.ordenEditando.numero_orden)}`, {
          method: 'PUT',
          body: payload
        });
        alert("Orden actualizada correctamente");
        await this.obtenerOrdenes();
        this.ordenEditando = null;
      } catch (error) {
        alert("Error al editar: " + (error.message || "desconocido"));
      }
    },

    // Edición de estado con prompt rápido
    async editarEstado(orden) {
      const nuevoEstado = prompt("Ingrese el nuevo estado (Activa, En pausa, Finalizada):");
      if (!nuevoEstado || !["Activa", "En pausa", "Finalizada"].includes(nuevoEstado)) {
        alert("Estado inválido. Debe ser 'Activa', 'En pausa' o 'Finalizada'.");
        return;
      }
      const password = prompt("Ingrese la contraseña para confirmar:");
      if (password !== "1234") {
        alert("Contraseña incorrecta.");
        return;
      }

      // Armamos payload completo desde la orden actual
      const base = { ...orden };
      if (nuevoEstado === "Finalizada" && !base.fecha_fin) {
        base.fecha_fin = this.formatFecha(new Date());
      }
      const payload = this.buildUpdatePayload({ ...base, estado: nuevoEstado });

      try {
        await apiFetch(`/update_orden/${encodeURIComponent(orden.numero_orden)}`, {
          method: 'PUT',
          body: payload
        });
        // actualizar localmente
        orden.estado = nuevoEstado;
        if (payload.fecha_fin) orden.fecha_fin = payload.fecha_fin;
      } catch (error) {
        alert("Error: " + (error.message || "No se pudo actualizar"));
      }
    },

    // Modal de estado
    abrirModalEstado(orden) {
      this.ordenEstadoEditando = {
        ...orden,
        fecha_fin: this.formatFecha(orden.fecha_fin)
      };
    },

    async guardarEstado() {
      const o = this.ordenEstadoEditando;
      if (o.estado === "Finalizada" && !o.fecha_fin) {
        o.fecha_fin = this.formatFecha(new Date());
      }
      const payload = this.buildUpdatePayload(o);

      try {
        await apiFetch(`/update_orden/${encodeURIComponent(o.numero_orden)}`, {
          method: 'PUT',
          body: payload
        });
        alert("Estado actualizado correctamente");
        await this.obtenerOrdenes();
        this.ordenEstadoEditando = null;
      } catch (error) {
        alert("Error al editar estado: " + (error.message || "desconocido"));
      }
    },

    goTo(routeName) {
      this.$router.push({ name: routeName });
    }
  }
};
</script>


<style scoped>
  .ordenes-container {
    width: 100%;
    margin: 20px auto;
    text-align: center;
  }
  
  .titulo {
    background-color: #b53b3b;
    color: white;
    padding: 10px;
    font-weight: bold;
  }
  
  .busqueda {
    width: 100%;
    padding: 8px;
    margin: 10px 0;
    border: 1px solid #ccc;
    border-radius: 5px;
  }
  
  .ordenes-tabla {
    width: 100%;
    border-collapse: collapse;
    margin-top: 10px;
  }
  
  /* Estilo para los encabezados de la tabla - mismo color que el título */
  .ordenes-tabla thead {
    background-color: #b53b3b;
    color: white;
  }
  
  th, td {
    border: 1px solid #ccc;
    padding: 8px;
    text-align: left;
  }
  
  .estado-activa {
    color: green;
    font-weight: bold;
  }
  
  .estado-pausa {
    color: orange;
    font-weight: bold;
  }
  
  .estado-finalizada {
    color: blue;
    font-weight: bold;
  }
  
  .editar-boton {
    background-color: #b53b3b;
    color: white;
    border: none;
    padding: 5px 10px;
    cursor: pointer;
    border-radius: 5px;
  }
  
  .guardar-boton {
    background-color: green;
    color: white;
    border: none;
    padding: 5px 10px;
    cursor: pointer;
    border-radius: 5px;
    margin-right: 5px;
  }
  
  .cancelar-boton {
    background-color: gray;
    color: white;
    border: none;
    padding: 5px 10px;
    cursor: pointer;
    border-radius: 5px;
  }
  
  .menu-boton-container {
    margin-top: 20px;
    text-align: center;
  }
  
  .menu-boton {
    padding: 10px 20px;
    font-size: 14px;
    background-color: #b53b3b;
    color: white;
    border: none;
    border-radius: 5px;
    cursor: pointer;
  }
  /* Estilos para los mensajes de estado */
.mensaje-estado {
    text-align: center;
    font-size: 1.2rem;
    margin: 10px;
    padding: 10px;
    border-radius: 5px;
    width: 50%;
    margin-left: auto;
    margin-right: auto;
}

.mensaje-exito {
    background-color: #d4edda;
    color: #155724;
    border: 1px solid #c3e6cb;
}

.mensaje-error {
    background-color: #f8d7da;
    color: #721c24;
    border: 1px solid #f5c6cb;
}
.modal {
  position: fixed; /* Hace que el modal flote sobre la pantalla */
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background-color: rgba(0, 0, 0, 0.5); /* Oscurece el fondo */
  display: flex;
  align-items: center;
  justify-content: center;
}

.modal-contenido {
  background: white;
  padding: 20px;
  width: 90%;
  max-width: 400px; /* Controla el ancho */
  border-radius: 8px;
  box-shadow: 0px 4px 10px rgba(0, 0, 0, 0.3);
  text-align: center;
}

.formulario {
  display: flex;
  flex-direction: column;
  gap: 10px; /* Espacio entre campos */
}

.input-field {
  width: 100%;
  padding: 8px;
  border: 1px solid #ccc;
  border-radius: 5px;
}

.botones {
  display: flex;
  justify-content: space-between;
  margin-top: 10px;
}

.btn {
  padding: 10px;
  border: none;
  cursor: pointer;
  border-radius: 5px;
}

.btn-guardar {
  background-color: #28a745;
  color: white;
}

.btn-cerrar {
  background-color: #dc3545;
  color: white;
}
</style>