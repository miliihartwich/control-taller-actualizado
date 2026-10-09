<template>
    <div class="usuarios">
      <h1>Lista de Usuarios</h1>
  
      <table>
        <thead>
          <tr>
            <th>Usuario</th>
            <th>Nombre del Empleado</th>
            <th>Rol</th>
            <th>Acción</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="usuario in usuarios" :key="usuario.usuario">
            <td>{{ usuario.usuario }}</td>
            <td>{{ usuario.nombre_empleado }}</td>
            <td>
              <select v-model="usuario.rol">
                <option value="propietario">Propietario</option>
                <option value="administracion">Administración</option>
                <option value="operario">Operario</option>
              </select>
            </td>
            <td>
              <button @click="actualizarRol(usuario)">Guardar</button>
            </td>
          </tr>
        </tbody>
      </table>

      <button @click="goTo('MenuPage')" class="btn">Menú</button>
  
      <div v-if="mensaje" :class="['mensaje', tipoMensaje]">
        {{ mensaje }}
      </div>
    </div>
  </template>
  
  <script>
import { apiFetch } from '@/api';

export default {
  name: 'UsuariosPage',
  data() {
    return {
      usuarios: [],
      mensaje: '',
      tipoMensaje: '' // 'exito' | 'error'
    };
  },

  methods: {
    async obtenerUsuarios() {
      try {
        const data = await apiFetch('/obtener_todos_usuarios'); // [{usuario, rol, nombre_empleado}]
        this.usuarios = data || [];
      } catch (error) {
        console.error('Error obteniendo usuarios:', error.message);
        this.mensaje = 'Error obteniendo usuarios';
        this.tipoMensaje = 'error';
      }
    },

    async actualizarRol(usuario) {
      try {
        const data = await apiFetch('/editar_rol', {
          method: 'PUT',
          body: { usuario: usuario.usuario, nuevo_rol: usuario.rol }
          // , auth: true  // <-- si luego protegés este endpoint con JWT
        });

        if (data?.success) {
          this.mensaje = 'Rol actualizado correctamente';
          this.tipoMensaje = 'exito';
        } else {
          this.mensaje = data?.message || 'Error al actualizar el rol';
          this.tipoMensaje = 'error';
        }
      } catch (error) {
        this.mensaje = error.message || 'Error de conexión con el servidor';
        this.tipoMensaje = 'error';
      } finally {
        // opcional: limpiar mensaje después de unos segundos
        setTimeout(() => (this.mensaje = ''), 3000);
      }
    },

    goTo(routeName) {
      this.$router.push({ name: routeName });
    },
  },

  mounted() {
    this.obtenerUsuarios();
  }
};
</script>

  
  <style scoped>
  .usuarios {
    text-align: center;
    padding: 20px;
  }
  
  h1 {
    font-size: 2rem;
    margin-bottom: 20px;
  }
  
  table {
    width: 100%;
    border-collapse: collapse;
    margin-top: 20px;
  }
  
  th, td {
    padding: 12px;
    border: 1px solid #ddd;
  }
  
  th {
    background-color: rgba(214, 15, 15, 0.8);
    color: white;
  }
  
  select {
    padding: 8px;
    font-size: 1rem;
  }
  
  button {
    background-color: rgba(214, 15, 15, 0.8);
    color: white;
    padding: 8px 12px;
    border: none;
    cursor: pointer;
  }
  
  button:hover {
    background-color: rgba(43, 0, 255);
  }
  
  .mensaje {
    margin-top: 20px;
    padding: 10px;
    border-radius: 5px;
    font-weight: bold;
  }
  
  .exito {
    background-color: #4caf50;
    color: white;
  }
  
  .error {
    background-color: #f44336;
    color: white;
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

  </style>
  