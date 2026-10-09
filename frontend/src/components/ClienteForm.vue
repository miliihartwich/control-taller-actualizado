<template>
    <div class="form-container">
      <h1 class="titulo">CLIENTE</h1>
  
      <div class="input-group">
        <label for="rut-ci">RUT/CI</label>
        <input v-model="cliente.rut_ci" type="text" id="rut-ci" placeholder="Type here..." />
      </div>
  
      <div class="input-group">
        <label for="nombre">Nombre</label>
        <input v-model="cliente.nombre" type="text" id="nombre" placeholder="Type here..." />
      </div>
  
      <div class="input-group">
        <label for="alias">Alias</label>
        <input v-model="cliente.alias" type="text" id="alias" placeholder="Type here..." />
      </div>
  
      <div class="input-group">
        <label for="telefono">Teléfono</label>
        <input v-model="cliente.telefono" type="text" id="telefono" placeholder="Type here..." />
      </div>
  
      <div class="input-group">
        <label for="whatsapp">Whatsapp</label>
        <input v-model="cliente.whatsapp" type="text" id="whatsapp" placeholder="Type here..." />
      </div>
  
      <div class="input-group">
        <label for="mail">Mail</label>
        <input v-model="cliente.mail" type="text" id="mail" placeholder="Type here..." />
      </div>
  
      <div class="input-group">
        <label for="departamento">Departamento</label>
        <select v-model="cliente.departamento" id="departamento" @change="cargarLocalidades">
          <option v-for="departamento in departamentos" :key="departamento" :value="departamento">{{ departamento }}</option>
        </select>
      </div>
  
      <div class="input-group">
        <label for="localidad">Localidad</label>
        <select v-model="cliente.localidad" id="localidad">
          <option v-for="localidad in localidades" :key="localidad" :value="localidad">{{ localidad }}</option>
        </select>
      </div>
  
      <div class="input-group">
        <label for="direccion">Dirección</label>
        <input v-model="cliente.direccion" type="text" id="direccion" placeholder="Type here..." />
      </div>
  
      <div class="buttons-container">
        <button class="btn" @click="guardarCliente">GUARDAR</button>
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
      cliente: {
        rut_ci: '',
        nombre: '',
        alias: '',
        telefono: '',
        whatsapp: '',
        mail: '',
        departamento: '',
        localidad: '',
        direccion: ''
      },
      departamentos: [],
      localidades: [],
      mensaje: '',
      exito: false
    };
  },

  created() {
    this.cargarDepartamentos();
  },

  watch: {
    'cliente.departamento'(nuevo) {
      if (nuevo) this.cargarLocalidades();
      else this.localidades = [];
    }
  },

  methods: {
    async cargarDepartamentos() {
      try {
        const data = await apiFetch('/departamentos');
        this.departamentos = data.departamentos; 
      } catch (error) {
        console.error('Error:', error.message);
      }
    },

    async cargarLocalidades() {
      try {
        if (!this.cliente.departamento) return;
        const data = await apiFetch(`/localidades?departamento=${encodeURIComponent(this.cliente.departamento)}`);
        this.localidades = data.localidades; 
      } catch (error) {
        console.error('Error:', error.message);
      }
    },

    async guardarCliente() {
      try {
        const data = await apiFetch('/cliente', {
          method: 'POST',
          body: this.cliente
          // auth: true, // descomenta si este endpoint requiere token
        });
        this.mensaje = data.message || 'Cliente creado exitosamente';
        this.exito = true;
        this.limpiarFormulario();
      } catch (error) {
        this.mensaje = error.message || 'Error al guardar el cliente.';
        this.exito = false;
      }
    },

    limpiarFormulario() {
      this.cliente = {
        rut_ci: '',
        nombre: '',
        alias: '',
        telefono: '',
        whatsapp: '',
        mail: '',
        departamento: '',
        localidad: '',
        direccion: ''
      };
      this.localidades = []; // limpiar también la lista
    },

    goTo(routeName) {
      this.$router.push({ name: routeName });
    },
  },
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
  </style>
  