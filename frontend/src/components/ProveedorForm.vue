<template>
    <div class="form-container">
      <h1 class="titulo">PROVEEDOR</h1>
  
      <div class="input-group">
        <label for="rut-ci">RUT/CI</label>
        <input v-model="proveedor.rut_ci" type="text" id="rut-ci" placeholder="Type here..." />
      </div>
  
      <div class="input-group">
        <label for="nombre">Nombre</label>
        <input v-model="proveedor.nombre" type="text" id="nombre" placeholder="Type here..." />
      </div>
  
      <div class="input-group">
        <label for="alias">Alias</label>
        <input v-model="proveedor.alias" type="text" id="alias" placeholder="Type here..." />
      </div>
  
      <div class="input-group">
        <label for="telefono">Teléfono</label>
        <input v-model="proveedor.telefono" type="text" id="telefono" placeholder="Type here..." />
      </div>
  
      <div class="input-group">
        <label for="whatsapp">Whatsapp</label>
        <input v-model="proveedor.whatsapp" type="text" id="whatsapp" placeholder="Type here..." />
      </div>
  
      <div class="input-group">
        <label for="mail">Mail</label>
        <input v-model="proveedor.mail" type="text" id="mail" placeholder="Type here..." />
      </div>
  
      <div class="input-group">
        <label for="departamento">Departamento</label>
        <select v-model="proveedor.departamento" id="departamento" @change="cargarLocalidades">
          <option v-for="departamento in departamentos" :key="departamento" :value="departamento">{{ departamento }}</option>
        </select>
      </div>
  
      <div class="input-group">
        <label for="localidad">Localidad</label>
        <select v-model="proveedor.localidad" id="localidad">
          <option v-for="localidad in localidades" :key="localidad" :value="localidad">{{ localidad }}</option>
        </select>
      </div>
  
      <div class="input-group">
        <label for="direccion">Dirección</label>
        <input v-model="proveedor.direccion" type="text" id="direccion" placeholder="Type here..." />
      </div>
  
      <div class="input-group">
        <label for="rubro">Rubro</label>
        <select v-model="proveedor.rubro" id="rubro">
          <option v-for="rubro in rubros" :key="rubro.id" :value="rubro.nombre">{{ rubro.nombre }}</option>
        </select>
        <button @click="mostrarCampoNuevoRubro" class="btn-nuevo">NUEVO</button>
      </div>
  
      <!-- Campo de Nuevo Rubro -->
      <div v-if="mostrarNuevoRubro" class="nuevo-rubro">
        <input v-model="nuevoRubroNombre" type="text" placeholder="Ingrese nuevo rubro..." />
        <button @click="guardarNuevoRubro" class="btn-guardar">Guardar</button>
        <button @click="cerrarNuevoRubro" class="btn-cerrar">Cerrar</button>
      </div>
  
      <div class="input-group">
        <label for="comentarios">Comentarios</label>
        <input v-model="proveedor.comentarios" type="text" id="comentarios" placeholder="Type here..." />
      </div>
  
      <div class="input-group">
        <label for="calificacion">Calificación</label>
        <select v-model="proveedor.calificacion" id="calificacion">
          <option v-for="n in 10" :key="n" :value="n">{{ n }}</option>
        </select>
      </div>
  
      <div class="buttons-container">
        <button class="btn" @click="guardarProveedor">GUARDAR</button>
        <button @click="goTo('MenuPage')" class="btn">Menú</button>
      </div>
  
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
      proveedor: {
        rut_ci: '',
        nombre: '',
        alias: '',
        telefono: '',
        whatsapp: '',
        mail: '',
        departamento: '',
        localidad: '',
        direccion: '',
        rubro: '',
        comentarios: '',
        calificacion: ''
      },
      departamentos: [],
      localidades: [],
      rubros: [],
      nuevoRubroNombre: '',
      mostrarNuevoRubro: false,
      mensaje: '',
      exito: false
    };
  },

  methods: {
    async cargarDepartamentos() {
      try {
        const data = await apiFetch('/departamentos');       // { departamentos: [...] }
        this.departamentos = data.departamentos || [];
      } catch (e) { console.error('Error:', e.message); }
    },

    async cargarLocalidades() {
      try {
        if (!this.proveedor.departamento) return;
        const qs = new URLSearchParams({ departamento: this.proveedor.departamento }).toString();
        const data = await apiFetch(`/localidades?${qs}`);   // { localidades: [...] }
        this.localidades = data.localidades || [];
      } catch (e) { console.error('Error:', e.message); }
    },

    async cargarRubros() {
      try {
        const data = await apiFetch('/rubros');              // { rubros: [{id, nombre}] }
        this.rubros = data.rubros || [];
      } catch (e) { console.error('Error:', e.message); }
    },

    mostrarCampoNuevoRubro() { this.mostrarNuevoRubro = true; },
    cerrarNuevoRubro() { this.mostrarNuevoRubro = false; this.nuevoRubroNombre = ''; },

    async guardarNuevoRubro() {
      if (!this.nuevoRubroNombre.trim()) {
        this.mensaje = 'Debe ingresar un nombre para el rubro.';
        this.exito = false;
        return;
      }
      try {
        await apiFetch('/rubroscrear', {
          method: 'POST',
          body: { rubro_nombre: this.nuevoRubroNombre }
        });
        this.mensaje = 'Rubro creado exitosamente.';
        this.exito = true;
        await this.cargarRubros();
        this.cerrarNuevoRubro();
      } catch (e) {
        this.mensaje = e.message || 'Error al crear el rubro.';
        this.exito = false;
      }
    },

    async guardarProveedor() {
      try {
        const data = await apiFetch('/proveedor', {
          method: 'POST',
          body: this.proveedor
        });
        this.mensaje = data.message || 'Proveedor creado exitosamente!';
        this.exito = true;
        this.limpiarFormulario();
      } catch (e) {
        this.mensaje = e.message || 'Error al guardar el proveedor.';
        this.exito = false;
      }
    },

    limpiarFormulario() {
      this.proveedor = {
        rut_ci: '',
        nombre: '',
        alias: '',
        telefono: '',
        whatsapp: '',
        mail: '',
        departamento: '',
        localidad: '',
        direccion: '',
        rubro: '',
        comentarios: '',
        calificacion: ''
      };
      this.localidades = [];
    },

    goTo(routeName) { this.$router.push({ name: routeName }); },
  },

  watch: {
    'proveedor.departamento'(nuevo) {
      if (nuevo) this.cargarLocalidades();
      else this.localidades = [];
    }
  },

  mounted() {
    this.cargarDepartamentos();
    this.cargarRubros();
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
  
  .input-group {
    margin-bottom: 20px;
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
  .nuevo-rubro-container {
    display: flex;
    align-items: center;
    gap: 10px;
    margin-top: 10px;
  }
  
  .nuevo-rubro-container input {
    flex-grow: 1;
    padding: 8px;
    border-radius: 4px;
    border: 1px solid #ccc;
  }
  
  .btn-guardar, .btn-cerrar {
    background-color: #4CAF50;
    color: white;
    border: none;
    padding: 8px 12px;
    cursor: pointer;
    border-radius: 4px;
  }
  
  .btn-cerrar {
    background-color: #f44336;
  }
  </style>
  