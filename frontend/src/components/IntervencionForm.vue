<template>
  <div class="form-container">
    <h1 class="titulo">REGISTRAR INTERVENCIÓN</h1>

    <form @submit.prevent="guardarIntervencion">
      <!-- Empleado -->
      <label>Empleado</label>
      <select v-model="intervencion.empleado">
        <option value="">Seleccione un empleado</option>
        <option v-for="empleado in empleados" :key="empleado.id" :value="empleado.nombre">
          {{ empleado.nombre }}
        </option>
      </select>

      <!-- División (ID) -->
      <label>División</label>
      <select v-model="intervencion.division_id" @change="onChangeDivision">
        <option value="">Seleccione una división</option>
        <option v-for="div in divisiones" :key="div.id" :value="div.id">
          {{ div.nombre }}
        </option>
      </select>

      <!-- Tipo (ID) -->
      <label>Tipo</label>
      <select
        v-model="intervencion.tipo_id"
        :disabled="!intervencion.division_id"
        @change="onChangeTipo"
      >
        <option value="">Seleccione un tipo</option>
        <option v-for="tipo in tipos" :key="tipo.id" :value="tipo.id">
          {{ tipo.nombre }}
        </option>
      </select>

      <!-- Descripción (ID) -->
      <label>Descripción</label>
      <select
        v-model="intervencion.descripcion_id"
        :disabled="!intervencion.tipo_id"
      >
        <option value="">Seleccione una descripción</option>
        <option
          v-for="desc in descripciones"
          :key="desc.id_descripcion"
          :value="desc.id_descripcion"
        >
          {{ desc.nombre_descripcion }}
        </option>
      </select>

      <!-- Fecha -->
      <label>Fecha</label>
      <input type="date" v-model="intervencion.fecha" />

      <!-- Hora Inicio -->
      <label>Hora Inicio</label>
      <input type="time" v-model="intervencion.hora_inicio" />

      <!-- Hora Fin -->
      <label>Hora Fin</label>
      <input type="time" v-model="intervencion.hora_fin" />

      <div class="buttons-container">
        <button class="btn" type="submit">GUARDAR</button>
        <button @click.prevent="goTo('MenuPage')" class="btn">Menú</button>
      </div>
    </form>

    <div v-if="mensaje" :class="['mensaje', exito ? 'exito' : 'error']">
      {{ mensaje }}
    </div>
  </div>
</template>

<script>
import { apiFetch } from '@/api';

export default {
  data() {
    return {
      intervencion: {
        empleado: "",
        division_id: "",
        tipo_id: "",
        descripcion_id: "",
        fecha: "",
        hora_inicio: "",
        hora_fin: ""
      },
      empleados: [],
      divisiones: [],     // [{id, nombre}]
      tipos: [],          // [{id, nombre}]
      descripciones: [],  // [{id_descripcion, nombre_descripcion}]
      mensaje: "",
      exito: false,
    };
  },

  computed: {
    divisionNombre() {
      const id = Number(this.intervencion.division_id);
      return this.divisiones.find(d => d.id === id)?.nombre || "";
    },
    tipoNombre() {
      const id = Number(this.intervencion.tipo_id);
      return this.tipos.find(t => t.id === id)?.nombre || "";
    },
    descripcionNombre() {
      const id = Number(this.intervencion.descripcion_id);
      return this.descripciones.find(d => d.id_descripcion === id)?.nombre_descripcion || "";
    }
  },

  methods: {
    async cargarEmpleados() {
      try {
        const data = await apiFetch('/obtener_empleados', { authWithCookies: true });
        this.empleados = Array.isArray(data) ? data : [];
      } catch (error) {
        console.error('Error al cargar empleados:', error.message || error);
      }
    },

    async cargarDivisiones() {
      try {
        const data = await apiFetch('/divisiones_id', { authWithCookies: true });
        this.divisiones = Array.isArray(data) ? data : [];
      } catch (error) {
        console.error('Error al cargar divisiones:', error.message || error);
      }
    },

    async cargarTiposPorDivisionId() {
      if (!this.intervencion.division_id) return;
      try {
        const data = await apiFetch(
          `/tipos_por_division_id/${encodeURIComponent(this.intervencion.division_id)}`,
          { authWithCookies: true }
        );
        this.tipos = Array.isArray(data) ? data : [];
      } catch (error) {
        console.error('Error al cargar tipos:', error.message || error);
      }
    },

    async cargarDescripcionesPorTipoId() {
      if (!this.intervencion.tipo_id) return;
      try {
        // opcional: pasar division_id como query param si implementaste validación en backend
        const data = await apiFetch(
          `/descripcion_por_tipo_id/${encodeURIComponent(this.intervencion.tipo_id)}?division_id=${encodeURIComponent(this.intervencion.division_id)}`,
          { authWithCookies: true }
        );
        this.descripciones = Array.isArray(data) ? data : [];
      } catch (error) {
        console.error('Error al cargar descripciones:', error.message || error);
      }
    },

    async onChangeDivision() {
      this.intervencion.tipo_id = "";
      this.intervencion.descripcion_id = "";
      this.tipos = [];
      this.descripciones = [];
      await this.cargarTiposPorDivisionId();
    },

    async onChangeTipo() {
      this.intervencion.descripcion_id = "";
      this.descripciones = [];
      await this.cargarDescripcionesPorTipoId();
    },

    async guardarIntervencion() {
      try {
        // Validación mínima
        if (!this.intervencion.empleado || !this.intervencion.division_id || !this.intervencion.tipo_id || !this.intervencion.descripcion_id) {
          this.mensaje = "Completá empleado, división, tipo y descripción.";
          this.exito = false;
          return;
        }

        // Payload por IDs + nombres (compatibilidad)
        const body = {
          empleado: this.intervencion.empleado,

          division_id: Number(this.intervencion.division_id),
          tipo_id: Number(this.intervencion.tipo_id),
          descripcion_id: Number(this.intervencion.descripcion_id),

          // opcional: si tu backend legacy lo usa
          division: this.divisionNombre,
          tipo: this.tipoNombre,
          descripcion: this.descripcionNombre,

          fecha: this.intervencion.fecha,
          hora_inicio: this.intervencion.hora_inicio,
          hora_fin: this.intervencion.hora_fin,
        };

        const data = await apiFetch('/intervenciones/registrar', {
          method: 'POST',
          body,
          authWithCookies: true,
        });

        this.mensaje = data?.message || 'Intervención creada exitosamente.';
        this.exito = true;
        this.limpiarFormulario();
      } catch (error) {
        console.error('Error al guardar intervención:', error.message || error);
        this.mensaje = error.message || 'Error al guardar la intervención.';
        this.exito = false;
      } finally {
        setTimeout(() => { this.mensaje = ''; }, 3000);
      }
    },

    limpiarFormulario() {
      this.intervencion = {
        empleado: "",
        division_id: "",
        tipo_id: "",
        descripcion_id: "",
        fecha: "",
        hora_inicio: "",
        hora_fin: ""
      };
      this.tipos = [];
      this.descripciones = [];
    },

    goTo(routeName) {
      this.$router.push({ name: routeName });
    },
  },

  async mounted() {
    await this.cargarDivisiones();
    await this.cargarEmpleados();
  }
};
</script>



  <style scoped>
  .form-container {
    width: 50%;
    margin: 0 auto;
  }

  .titulo {
    background-color: #b53b3b;
    color: white;
    padding: 10px;
    text-align: center;
    border-radius: 4px;
  }

  label {
    display: block;
    font-size: 1.2rem;
  }

  input, select {
    width: 100%;
    padding: 10px;
    font-size: 1rem;
    border-radius: 4px;
    border: 1px solid #ccc;
  }

  .buttons-container {
    display: flex;
    justify-content: space-between;
    margin-top: 20px;
  }

  .btn {
    background-color: #b53b3b;
    color: white;
    font-size: 1.2rem;
    padding: 10px 20px;
    cursor: pointer;
    border: none;
    border-radius: 4px;
  }

  .mensaje {
    margin-top: 20px;
    padding: 10px;
    border-radius: 4px;
    font-weight: bold;
    text-align: center;
  }

  .exito {
    background-color: #4caf50;
    color: white;
  }

  .error {
    background-color: #f44336;
    color: white;
  }
  </style>