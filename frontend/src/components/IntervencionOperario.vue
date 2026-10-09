<template>
  <div class="form-container">
    <h1 class="titulo">INTERVENCIÓN</h1>

    <label>Operario</label>
    <input type="text" v-model="cedulaUsuario" disabled />

    <label for="division">División</label>
    <select
      id="division"
      v-model.number="intervencion.division_id"
      @change="onChangeDivision(); limpiarMensaje()"
    >
      <option :value="''">Seleccione una división</option>
      <option v-for="div in divisiones" :key="div.id" :value="Number(div.id)">
        {{ div.nombre }}
      </option>
    </select>
    <label for="tipo">Tipo</label>
    <select
      id="tipo"
      v-model.number="intervencion.tipo_id"
      :disabled="!intervencion.division_id"
      @change="onChangeTipo(); limpiarMensaje()"
    >
      <option :value="''">Seleccione un tipo</option>
      <option v-for="tipo in tipos" :key="tipo.id" :value="Number(tipo.id)">
        {{ tipo.nombre }}
      </option>
    </select>
    <label for="descripcion">Descripción</label>
    <select
      id="descripcion"
      v-model.number="intervencion.descripcion_id"
      :disabled="!intervencion.tipo_id"
      @change="limpiarMensaje"
    >
      <option :value="''">Seleccione una descripción</option>
      <option
        v-for="desc in descripciones"
        :key="Number(desc.id_descripcion)"
        :value="Number(desc.id_descripcion)"
      >
        {{ desc.nombre_descripcion }}
      </option>
    </select>

    <div class="buttons-container">
      <button @click="goTo('OrdenesForm')" class="btn btn-red">Nueva Orden</button>
    </div>

    <!-- Estado: NO hay intervención en curso -->
    <div v-if="!mostrandoIntervencion">
      <button class="btn btn-red" @click="iniciarIntervencion(); limpiarMensaje()">
        Inicio intervención
      </button>
    </div>

    <!-- Estado: HAY intervención en curso -->
    <div v-if="mostrandoIntervencion">
      <label for="fecha">Fecha</label>
      <input id="fecha" type="text" v-model="intervencion.fecha" disabled />

      <label for="hora-inicio">Hora inicio</label>
      <input id="hora-inicio" type="text" v-model="intervencion.hora_inicio" disabled />

      <div class="buttons-container">
        <button class="btn btn-red" @click="finalizarIntervencion">
          Finalizar Intervención
        </button>
      </div>

      <label for="hora-fin">Hora fin</label>
      <input id="hora-fin" type="text" v-model="intervencion.hora_fin" disabled />
    </div>

    <div v-if="mensaje" :class="['mensaje', exito ? 'mensaje-exito' : 'mensaje-error']">
      {{ mensaje }}
    </div>

    <div class="buttons-container">
      <button class="btn" @click="nuevaIntervencion">Nueva intervención</button>
      <button class="btn" @click="confirmarCerrarSesion">Cerrar sesión</button>
      <button class="btn" @click="goTo('CambiarContrasena')">Cambiar Contraseña</button>
    </div>
  </div>
</template>

<script>
import { apiFetch } from '@/api';

export default {
  name: 'IntervencionOperario',
  data() {
    return {
      divisiones: [],     // [{id, nombre}]
      tipos: [],          // [{id, nombre}]
      descripciones: [],  // [{id_descripcion, nombre_descripcion}]
      intervencion: {
        division_id: '',
        tipo_id: '',
        descripcion_id: '',
        // (los nombres los derivamos desde los arrays)
        fecha: '',
        hora_inicio: '',
        hora_fin: '',
      },
      ultimaIntervencion: { division_id: '', tipo_id: '', descripcion_id: '' },
      mensaje: '',
      exito: false,
      mostrandoIntervencion: false,
      cedulaUsuario: localStorage.getItem('cedula') || '',
      _visHandler: null,
    };
  },

  computed: {
    divisionNombre() {
      const id = Number(this.intervencion.division_id);
      return this.divisiones.find(d => d.id === id)?.nombre || '';
    },
    tipoNombre() {
      const id = Number(this.intervencion.tipo_id);
      return this.tipos.find(t => t.id === id)?.nombre || '';
    },
    descripcionNombre() {
      const id = Number(this.intervencion.descripcion_id);
      return this.descripciones.find(d => Number(d.id_descripcion) === id)?.nombre_descripcion || '';
    },
  },

  methods: {
    // -------- navegación / UI ----------
    goTo(routeName) {
      this.limpiarMensaje();
      this.$router.push({ name: routeName });
    },

    limpiarMensaje() {
      this.mensaje = '';
      this.exito = false;
    },

    // -------- util ----------
    _hhmmss(d = new Date()) {
      return d.toLocaleTimeString('es-ES', {
        hour12: false,
        hour: '2-digit',
        minute: '2-digit',
        second: '2-digit',
      });
    },

    // -------- catálogos (IDs) ----------
    async cargarDivisiones() {
      try {
        const data = await apiFetch('/divisiones_id', { authWithCookies: true });
        this.divisiones = Array.isArray(data) ? data : [];
      } catch (e) {
        console.error(e?.message || e);
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
      } catch (e) {
        console.error(e?.message || e);
      }
    },

    async cargarDescripcionesPorTipoId() {
      if (!this.intervencion.tipo_id) return;
      try {
        const data = await apiFetch(
          `/descripcion_por_tipo_id/${encodeURIComponent(this.intervencion.tipo_id)}`,
          { authWithCookies: true }
        );
        this.descripciones = Array.isArray(data) ? data : [];
      } catch (e) {
        console.error(e?.message || e);
      }
    },

    onChangeDivision() {
      // reset dependencias
      this.intervencion.tipo_id = '';
      this.intervencion.descripcion_id = '';
      this.tipos = [];
      this.descripciones = [];
      this.cargarTiposPorDivisionId();
    },

    onChangeTipo() {
      // reset dependencias
      this.intervencion.descripcion_id = '';
      this.descripciones = [];
      this.cargarDescripcionesPorTipoId();
    },

    // -------- rehidratación de abierta ----------
    async cargarIntervencionAbierta() {
      try {
        const resp = await apiFetch('/intervenciones/abierta', { authWithCookies: true });
        const abierta = resp?.abierta || null;

        if (abierta) {
          // OJO: tu backend hoy devuelve nombres, no ids.
          // Para no romper, seguimos poblando NOMBRES en el UI si vienen.
          // Si después migrás backend a ids, ajustamos acá.
          this._poblarDesdeAbierta(abierta);
        } else {
          this.mostrandoIntervencion = false;
          this.intervencion.hora_fin = '';
        }
      } catch (e) {
        if (e?.status === 401) {
          this.$router.push({ name: 'Login' });
        } else {
          console.warn('No se pudo cargar intervención abierta:', e?.message || e);
        }
      }
    },

    _poblarDesdeAbierta(abierta) {
      // Si abierta trae nombres, intentamos mapearlos a ids:
      // division
      if (abierta.division) {
        const foundDiv = this.divisiones.find(d => d.nombre === abierta.division);
        this.intervencion.division_id = foundDiv ? foundDiv.id : '';
      }

      // tipo: necesitamos tipos cargados antes
      // por eso: cargamos tipos y después mapeamos tipo/descripcion
      this.intervencion.fecha = abierta.fecha || new Date().toISOString().slice(0, 10);
      this.intervencion.hora_inicio = abierta.hora_inicio || '';
      this.intervencion.hora_fin = '';
      this.mostrandoIntervencion = true;
    },

    // -------- acciones ----------
    async iniciarIntervencion() {
      if (!this.intervencion.division_id || !this.intervencion.tipo_id || !this.intervencion.descripcion_id) {
        this.mensaje = 'Completá división, tipo y descripción antes de iniciar.';
        this.exito = false;
        return;
      }

      const now = new Date();
      this.intervencion.fecha = now.toISOString().split('T')[0];
      this.intervencion.hora_inicio = this._hhmmss(now);
      this.intervencion.hora_fin = '';

      try {
        // Mandamos IDs + también nombres (por compatibilidad si el backend aún busca por strings)
        const body = {
          division_id: Number(this.intervencion.division_id),
          tipo_id: Number(this.intervencion.tipo_id),
          descripcion_id: Number(this.intervencion.descripcion_id),

          division: (this.divisionNombre || '').trim(),
          tipo: (this.tipoNombre || '').trim(),
          descripcion: (this.descripcionNombre || '').trim(),

          fecha: this.intervencion.fecha,
          hora_inicio: this.intervencion.hora_inicio,
        };

        await apiFetch('/intervenciones/iniciar', { method: 'POST', body, authWithCookies: true });

        this.mostrandoIntervencion = true;
        this.mensaje = 'Intervención iniciada';
        this.exito = true;
      } catch (e) {
        this.mensaje = e?.message || 'No se pudo iniciar la intervención';
        this.exito = false;
      } finally {
        setTimeout(() => (this.mensaje = ''), 2500);
      }
    },

    async finalizarIntervencion() {
      const hora_fin = this._hhmmss(new Date());

      try {
        await apiFetch('/intervenciones/cerrar', {
          method: 'PUT',
          body: { hora_fin },
          authWithCookies: true,
        });

        this.mensaje = 'Intervención finalizada';
        this.exito = true;
      } catch (e) {
        this.mensaje = e?.message || 'No se pudo finalizar la intervención';
        this.exito = false;
      } finally {
        this.mostrandoIntervencion = false;
        setTimeout(() => (this.mensaje = ''), 2500);
      }
    },

    async nuevaIntervencion() {
      if (this.mostrandoIntervencion) {
        await this.finalizarIntervencion();
      }

      this.ultimaIntervencion = {
        division_id: this.intervencion.division_id,
        tipo_id: this.intervencion.tipo_id,
        descripcion_id: this.intervencion.descripcion_id,
      };

      this.intervencion = {
        division_id: this.ultimaIntervencion.division_id || '',
        tipo_id: this.ultimaIntervencion.tipo_id || '',
        descripcion_id: this.ultimaIntervencion.descripcion_id || '',
        fecha: '',
        hora_inicio: '',
        hora_fin: '',
      };

      await this.iniciarIntervencion();
    },

    confirmarCerrarSesion() {
      if (!window.confirm('¿Seguro que querés cerrar sesión?')) return;

      localStorage.removeItem('usuario');
      localStorage.removeItem('rol');
      localStorage.removeItem('cedula');

      // legacy
      localStorage.removeItem('token');
      localStorage.removeItem('access_token');
      localStorage.removeItem('jwt');
      sessionStorage.removeItem('token');
      sessionStorage.removeItem('access_token');
      sessionStorage.removeItem('jwt');

      window.location.href = '/login';
    },
  },

  async mounted() {
    // catálogos primero (necesario para mapear abierta)
    await this.cargarDivisiones();

    // levantar intervención abierta si existe
    await this.cargarIntervencionAbierta();

    // re-chequear cuando vuelve al primer plano
    this._visHandler = () => {
      if (document.visibilityState === 'visible') this.cargarIntervencionAbierta();
    };
    document.addEventListener('visibilitychange', this._visHandler);
  },

  beforeUnmount() {
    if (this._visHandler) document.removeEventListener('visibilitychange', this._visHandler);
  },
};
</script>

<style scoped>
.form-container {
  width: 90%; 
  max-width: 500px; /* No demasiado ancho en pantallas grandes */
  margin: 0 auto;
  padding: 20px;
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
    margin-top: 10px;
  }

  input, select {
    width: 100%;
    padding: 10px;
    font-size: 1rem;
    border-radius: 4px;
    border: 1px solid #ccc;
    margin-top: 5px;
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
    text-align: center;
    flex-grow: 1;
    margin: 5px;
  width: 100%;
  display: block;
}


  .mensaje {
  text-align: center;
  font-size: 1rem;
  font-weight: bold;
  padding: 10px;
  margin: 10px 0;
  border-radius: 4px;
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

</style>