<template>
  <div class="form-container">
    <h1 class="titulo">EMPLEADO</h1>

    <div class="input-group">
      <label for="cedula">Cédula</label>
      <input v-model="empleado.cedula" type="text" id="cedula" placeholder="Type here..." />
    </div>

    <div class="input-group">
      <label for="nombre">Nombre</label>
      <input v-model="empleado.nombre" type="text" id="nombre" placeholder="Type here..." />
    </div>

    <div class="input-group">
      <label for="celular">Celular</label>
      <input v-model="empleado.celular" type="text" id="celular" placeholder="Type here..." />
    </div>

    <div class="input-group">
      <label for="factor">Factor</label>
      <input v-model="empleado.factor" type="text" id="factor" placeholder="Type here..." />
    </div>

    <div class="input-group">
      <label for="direccion">Dirección</label>
      <input v-model="empleado.direccion" type="text" id="direccion" placeholder="Type here..." />
    </div>

    <div class="input-group">
      <label for="remuneracion">Remuneración</label>
      <input v-model="empleado.remuneracion" type="text" id="remuneracion" placeholder="Type here..." />
    </div>

    <div class="input-group">
      <label for="fecha_vencimiento_carnet">Fecha Vencimiento Carnet</label>
      <input v-model="empleado.fecha_vencimiento_carnet" type="date" id="fecha_vencimiento_carnet" />
    </div>

    <div class="buttons-container">
      <button class="btn" @click="guardarEmpleado">GUARDAR</button>
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
      empleado: {
        cedula: '',
        nombre: '',
        celular: '',
        factor: '',
        direccion: '',
        remuneracion: '',
        fecha_vencimiento_carnet: ''
      },
      mensaje: '',
      exito: false
    };
  },
  methods: {
    async guardarEmpleado() {
      try {
        const data = await apiFetch('/empleado', {
          method: 'POST',
          body: this.empleado
        });

        this.mensaje = data.message || 'Empleado creado exitosamente';
        this.exito = true;
        this.limpiarFormulario();
      } catch (error) {
        this.mensaje = error.message || 'Error al guardar el empleado.';
        this.exito = false;
      } finally {
        setTimeout(() => { this.mensaje = ''; }, 3000); // opcional
      }
    },

    limpiarFormulario() {
      this.empleado = {
        cedula: '',
        nombre: '',
        celular: '',
        factor: '',
        direccion: '',
        remuneracion: '',
        fecha_vencimiento_carnet: ''
      };
    },

    goTo(routeName) {
      this.$router.push({ name: routeName });
    },
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

input {
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
  background-color: rgba(214, 15, 15, 0.8);
  color: white;
  font-size: 1.2rem;
  padding: 10px 20px;
  cursor: pointer;
  border: none;
  border-radius: 4px;
}

.btn:hover {
  background-color: rgba(43, 0, 255, 0.8);
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
