<template>
  <div class="proveedores-container">
    <h1 class="titulo">Listado de Divisiones y Tipos</h1>
    
    <div class="busqueda-container">
      <input 
        type="text" 
        class="busqueda" 
        :placeholder="obtenerPlaceholder()"
        v-model="busqueda"
      />
      
      <div class="botones-busqueda">
        <button 
          class="boton-filtro" 
          :class="{ 'activo': tipoBusqueda === 'division' }"
          @click="cambiarTipoBusqueda('division')"
        >
          Buscar por División
        </button>
        <button 
          class="boton-filtro" 
          :class="{ 'activo': tipoBusqueda === 'tipo' }"
          @click="cambiarTipoBusqueda('tipo')"
        >
          Buscar por Tipo
        </button>
        <button 
          class="boton-filtro" 
          :class="{ 'activo': tipoBusqueda === 'descripcion' }"
          @click="cambiarTipoBusqueda('descripcion')"
        >
          Buscar por Descripción
        </button>
      </div>
    </div>
    
    <div v-if="cargando" class="cargando">
      <p>Cargando datos...</p>
    </div>
    
    <div v-else-if="error" class="error-mensaje">
      <p>{{ error }}</p>
    </div>
    
    <div v-else-if="buscando" class="cargando">
      <p>Buscando...</p>
    </div>
    
    <div v-else class="listado">
      <!-- Búsqueda por tipo: mostrar directamente los tipos encontrados -->
      <div v-if="tipoBusqueda === 'tipo' && busqueda && !sinResultados" class="resultados-directos">
        <h3>Tipos encontrados:</h3>
        <div v-for="(tipoInfo, index) in tiposEncontradosDirectos" :key="'tipo-directo-'+index" class="tipo-item-directo">
          <div class="tipo-header active">
            <span>{{ tipoInfo.tipo }} (División: {{ tipoInfo.division }})</span>
          </div>
          <div class="descripcion-container">
            <div v-if="cargandoDescripciones" class="cargando-item">
              <p>Cargando descripciones...</p>
            </div>
            <div v-else-if="!tipoInfo.descripciones || tipoInfo.descripciones.length === 0" class="sin-datos">
              <p>No hay descripciones disponibles para este tipo</p>
            </div>
            <div v-else>
              <div v-for="(descripcion, descIndex) in tipoInfo.descripciones" :key="descIndex" class="descripcion-item">
                <p>{{ descripcion }}</p>
              </div>
            </div>
          </div>
        </div>
      </div>
      
      <!-- Búsqueda por descripción: mostrar directamente las descripciones encontradas -->
      <div v-if="tipoBusqueda === 'descripcion' && busqueda && !sinResultados" class="resultados-directos">
        <h3>Descripciones encontradas:</h3>
        <div v-for="(descInfo, index) in descripcionesEncontradasDirectas" :key="'desc-directo-'+index" class="descripcion-item-directo">
          <div class="tipo-header active">
            <span>{{ descInfo.descripcion }}</span>
          </div>
          <div class="info-container">
            <p>Tipo: {{ descInfo.tipo }} | División: {{ descInfo.division }}</p>
          </div>
        </div>
      </div>
      
      <!-- Listado normal de divisiones -->
      <div v-for="(division, index) in divisionesFiltradas" :key="index" class="division-item">
        <div 
          class="division-header" 
          @click="cargarTipos(division)"
          :class="{ 'active': divisionSeleccionada === division }"
        >
          <span>{{ division }}</span>
          <span class="toggle-icon">{{ divisionSeleccionada === division ? '▼' : '►' }}</span>
        </div>
        
        <div v-if="divisionSeleccionada === division" class="tipos-container">
          <div v-if="cargandoTipos" class="cargando-item">
            <p>Cargando tipos...</p>
          </div>
          
          <div v-else-if="errorTipos" class="error-item">
            <p>{{ errorTipos }}</p>
          </div>
          
          <div v-else-if="tiposPorDivision.length === 0" class="sin-datos">
            <p>No hay tipos disponibles para esta división</p>
          </div>
          
          <div 
            v-else
            v-for="(tipo, tipoIndex) in tiposPorDivision" 
            :key="tipoIndex" 
            class="tipo-item"
          >
            <div 
              class="tipo-header" 
              @click="cargarDescripciones(tipo)"
              :class="{ 'active': tipoSeleccionado === tipo }"
            >
              <span>{{ tipo }}</span>
              <span class="toggle-icon">{{ tipoSeleccionado === tipo ? '▼' : '►' }}</span>
            </div>
            
            <div v-if="tipoSeleccionado === tipo" class="descripcion-container">
              <div v-if="cargandoDescripciones" class="cargando-item">
                <p>Cargando descripciones...</p>
              </div>
              
              <div v-else-if="errorDescripciones" class="error-item">
                <p>{{ errorDescripciones }}</p>
              </div>
              
              <div v-else-if="descripcionesPorTipo.length === 0" class="sin-datos">
                <p>No hay descripciones disponibles para este tipo</p>
              </div>
              
              <div v-else>
                <div v-for="(descripcion, descIndex) in descripcionesPorTipo" :key="descIndex" class="descripcion-item">
                  <p>{{ descripcion }}</p>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
    
    <div v-if="sinResultados" class="sin-resultados">
      <p>No se encontraron resultados para la búsqueda: "{{ busqueda }}"</p>
    </div>
    
    <!-- Botón de Menú -->
    <div class="menu-boton-container">
      <button @click="goTo('MenuPage')" class="menu-boton">Menú</button>
    </div>        
    <div v-if="mensajeExito" class="mensaje">
      {{ mensajeExito }}
    </div>
  </div>
</template>

<script>
import { apiFetch } from '@/api';

export default {
  name: 'DivisionesTipos',
  data() {
    return {
      divisiones: [],
      tiposPorDivision: [],
      descripcionesPorTipo: [],
      divisionSeleccionada: null,
      tipoSeleccionado: null,
      busqueda: '',
      tipoBusqueda: 'division', // 'division' | 'tipo' | 'descripcion'
      mensajeExito: '',
      cargando: true,
      error: null,
      cargandoTipos: false,
      errorTipos: null,
      cargandoDescripciones: false,
      errorDescripciones: null,
      buscando: false,
      sinResultados: false,
      resultadosBusqueda: { divisiones: [], tipos: {}, descripciones: {} },
      tiposEncontradosDirectos: [],
      descripcionesEncontradasDirectas: []
    };
  },

  computed: {
    divisionesFiltradas() {
      if (!this.busqueda) return this.divisiones;
      if (this.resultadosBusqueda.divisiones.length > 0) return this.resultadosBusqueda.divisiones;
      return this.divisiones;
    }
  },

  created() {
    this.cargarDivisiones();
  },

  watch: {
    busqueda(newVal) {
      if (newVal) {
        this.realizarBusqueda();
      } else {
        this.resultadosBusqueda = { divisiones: [], tipos: {}, descripciones: {} };
        this.tiposEncontradosDirectos = [];
        this.descripcionesEncontradasDirectas = [];
        this.divisionSeleccionada = null;
        this.tipoSeleccionado = null;
        this.sinResultados = false;
      }
    }
  },

  methods: {
    obtenerPlaceholder() {
      switch (this.tipoBusqueda) {
        case 'division': return 'Buscar por nombre de división...';
        case 'tipo': return 'Buscar por nombre de tipo...';
        case 'descripcion': return 'Buscar por descripción...';
        default: return 'Buscar...';
      }
    },

    cambiarTipoBusqueda(tipo) {
      this.tipoBusqueda = tipo;
      this.tiposEncontradosDirectos = [];
      this.descripcionesEncontradasDirectas = [];
      if (this.busqueda) this.realizarBusqueda();
    },

    async cargarDivisiones() {
      this.cargando = true; this.error = null;
      try {
        this.divisiones = await apiFetch('/divisiones'); // ← base tomada de VITE_API_BASE_URL
      } catch (err) {
        console.error(err);
        this.error = 'No se pudieron cargar las divisiones. Por favor, intente nuevamente.';
      } finally {
        this.cargando = false;
      }
    },

    async cargarTipos(division) {
      // toggle
      if (this.divisionSeleccionada === division) {
        this.divisionSeleccionada = null;
        this.tiposPorDivision = [];
        this.tipoSeleccionado = null;
        this.descripcionesPorTipo = [];
        return;
      }

      this.divisionSeleccionada = division;
      this.tipoSeleccionado = null;
      this.descripcionesPorTipo = [];
      this.cargandoTipos = true; this.errorTipos = null;

      if (this.busqueda && this.resultadosBusqueda.tipos[division]) {
        this.tiposPorDivision = this.resultadosBusqueda.tipos[division];
        this.cargandoTipos = false;
        return;
      }

      try {
        this.tiposPorDivision = await apiFetch(`/tipos_por_division/${encodeURIComponent(division)}`);
      } catch (err) {
        console.error(err);
        this.errorTipos = 'No se pudieron cargar los tipos. Por favor, intente nuevamente.';
      } finally {
        this.cargandoTipos = false;
      }
    },

    async cargarDescripciones(tipo) {
      // toggle
      if (this.tipoSeleccionado === tipo) {
        this.tipoSeleccionado = null;
        this.descripcionesPorTipo = [];
        return;
      }

      this.tipoSeleccionado = tipo;
      this.cargandoDescripciones = true; this.errorDescripciones = null;

      if (this.busqueda && this.resultadosBusqueda.descripciones[tipo]) {
        this.descripcionesPorTipo = this.resultadosBusqueda.descripciones[tipo];
        this.cargandoDescripciones = false;
        return;
      }

      try {
        this.descripcionesPorTipo = await apiFetch(`/descripcion_por_tipo/${encodeURIComponent(tipo)}`);
      } catch (err) {
        console.error(err);
        this.errorDescripciones = 'No se pudieron cargar las descripciones. Por favor, intente nuevamente.';
      } finally {
        this.cargandoDescripciones = false;
      }
    },

    // util para ordenar coincidencias (empieza con → contiene)
    ordenarResultadosBusqueda(items, busquedaLower) {
      const comienzan = [];
      const contienen = [];
      items.forEach(i => {
        const s = (i || '').toLowerCase();
        if (s.startsWith(busquedaLower)) comienzan.push(i);
        else if (s.includes(busquedaLower)) contienen.push(i);
      });
      return [...comienzan, ...contienen];
    },

    async realizarBusqueda() {
      if (!this.busqueda) return;
      this.buscando = true; this.sinResultados = false;

      this.resultadosBusqueda = { divisiones: [], tipos: {}, descripciones: {} };
      this.tiposEncontradosDirectos = [];
      this.descripcionesEncontradasDirectas = [];

      const q = this.busqueda.toLowerCase();

      try {
        if (this.tipoBusqueda === 'division') {
          await this.buscarPorDivision(q);
        } else if (this.tipoBusqueda === 'tipo') {
          await this.buscarPorTipo(q);
        } else {
          await this.buscarPorDescripcion(q);
        }

        const noDiv = this.resultadosBusqueda.divisiones.length === 0;
        const noTipo = this.tiposEncontradosDirectos.length === 0;
        const noDesc = this.descripcionesEncontradasDirectas.length === 0;

        this.sinResultados =
          (this.tipoBusqueda === 'division' && noDiv) ||
          (this.tipoBusqueda === 'tipo' && noTipo) ||
          (this.tipoBusqueda === 'descripcion' && noDesc);
      } catch (e) {
        console.error('Error en la búsqueda:', e);
      } finally {
        this.buscando = false;
      }
    },

    async buscarPorDivision(q) {
      const comienzan = [];
      const contienen = [];
      this.divisiones.forEach(div => {
        const s = div.toLowerCase();
        if (s.startsWith(q)) comienzan.push(div);
        else if (s.includes(q)) contienen.push(div);
      });
      this.resultadosBusqueda.divisiones = [...comienzan, ...contienen];
    },

async buscarPorTipo(q) {
  this.tiposEncontradosDirectos = [];

  for (const division of this.divisiones) {
    try {
      const tipos = await apiFetch(`/tipos_por_division/${encodeURIComponent(division)}`);
      const filtrados = this.ordenarResultadosBusqueda(Array.isArray(tipos) ? tipos : [], q);

      if (filtrados.length === 0) continue;

      if (!this.resultadosBusqueda.divisiones.includes(division)) {
        this.resultadosBusqueda.divisiones.push(division);
      }
      this.resultadosBusqueda.tipos[division] = filtrados;

      for (const tipo of filtrados) {
        try {
          const descripciones =
            await apiFetch(`/descripcion_por_tipo/${encodeURIComponent(tipo)}`);
          this.tiposEncontradosDirectos.push({
            tipo,
            division,
            descripciones: Array.isArray(descripciones) ? descripciones : []
          });
        } catch (e) {
          // Log y seguimos; añadimos igualmente el tipo con descripciones vacías
          console.debug('No se pudieron cargar descripciones', { division, tipo, error: e?.message || e });
          this.tiposEncontradosDirectos.push({ tipo, division, descripciones: [] });
          continue;
        }
      }
    } catch (e) {
      // Log y continuamos con la siguiente división
      console.debug('No se pudieron cargar tipos para la división', { division, error: e?.message || e });
      continue;
    }
  }
},
async buscarPorDescripcion(q) {
  this.descripcionesEncontradasDirectas = [];

  for (const division of this.divisiones) {
    try {
      const tiposResp = await apiFetch(`/tipos_por_division/${encodeURIComponent(division)}`);
      const tipos = Array.isArray(tiposResp) ? tiposResp : [];
      if (tipos.length === 0) continue;

      for (const tipo of tipos) {
        try {
          const descResp = await apiFetch(`/descripcion_por_tipo/${encodeURIComponent(tipo)}`);
          const descripciones = Array.isArray(descResp) ? descResp : [];
          const filtradas = this.ordenarResultadosBusqueda(descripciones, q);
          if (filtradas.length === 0) continue;

          if (!this.resultadosBusqueda.divisiones.includes(division)) {
            this.resultadosBusqueda.divisiones.push(division);
          }
          if (!this.resultadosBusqueda.tipos[division]) {
            this.resultadosBusqueda.tipos[division] = [];
          }
          if (!this.resultadosBusqueda.tipos[division].includes(tipo)) {
            this.resultadosBusqueda.tipos[division].push(tipo);
          }
          this.resultadosBusqueda.descripciones[tipo] = filtradas;

          for (const descripcion of filtradas) {
            this.descripcionesEncontradasDirectas.push({ descripcion, tipo, division });
          }
        } catch (e) {
          console.debug('No se pudieron cargar descripciones', { division, tipo, error: e?.message || e });
          continue;
        }
      }
    } catch (e) {
      console.debug('No se pudieron cargar tipos para la división', { division, error: e?.message || e });
      continue;
    }
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
  
  /* Contenedor de búsqueda */
  .busqueda-container {
    margin-bottom: 20px;
  }
  
  /* Input de búsqueda */
  .busqueda {
    width: 100%;
    padding: 10px;
    margin-bottom: 10px;
    border: 1px solid #ccc;
    border-radius: 5px;
    font-size: 1rem;
  }
  
  /* Botones de búsqueda */
  .botones-busqueda {
    display: flex;
    justify-content: center;
    flex-wrap: wrap;
    gap: 10px;
    margin-bottom: 15px;
  }
  
  .boton-filtro {
    padding: 8px 15px;
    background-color: #f0f0f0;
    border: 1px solid #ddd;
    border-radius: 5px;
    cursor: pointer;
    font-size: 0.9rem;
    transition: all 0.2s;
  }
  
  .boton-filtro:hover {
    background-color: #e0e0e0;
  }
  
  .boton-filtro.activo {
    background-color: #b53b3b;
    color: white;
    border-color: #992f2f;
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
    margin-top: 20px;
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
    position: fixed;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    background: rgba(0, 0, 0, 0.5);
    display: flex;
    justify-content: center;
    align-items: center;
    z-index: 1000;
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
  
  /* Estilos específicos para la jerarquía de divisiones y tipos */
  .listado {
    margin-top: 20px;
    text-align: left;
    border: 1px solid #ddd;
    border-radius: 5px;
    overflow: hidden;
  }
  
  .division-item {
    border-bottom: 1px solid #eee;
  }
  
  .division-header {
    background-color: #f8f8f8;
    padding: 12px 15px;
    cursor: pointer;
    display: flex;
    justify-content: space-between;
    font-weight: bold;
    transition: background-color 0.2s;
  }
  
  .division-header:hover, .division-header.active {
    background-color: #e8e8e8;
  }
  
  .division-header.active {
    background-color: #b53b3b;
    color: white;
  }
  
  .tipos-container {
    padding-left: 20px;
  }
  
  .tipo-item {
    border-bottom: 1px solid #f0f0f0;
  }
  
  .tipo-header {
    padding: 10px 15px;
    cursor: pointer;
    display: flex;
    justify-content: space-between;
    transition: background-color 0.2s;
  }
  
  .tipo-header:hover, .tipo-header.active {
    background-color: #f0f0f0;
  }
  
  .tipo-header.active {
    background-color: #d88a8a;
    color: white;
  }
  
  .descripcion-container {
    padding: 10px 15px 10px 30px;
    background-color: #f9f9f9;
    border-top: 1px solid #eee;
  }
  
  .toggle-icon {
    font-size: 12px;
  }
  
  /* Estilos para estados de carga y error */
  .cargando, .error-mensaje, .sin-datos, .sin-resultados {
    padding: 20px;
    text-align: center;
    border: 1px solid #ddd;
    border-radius: 5px;
    margin-top: 20px;
  }
  
  .cargando {
    background-color: #f8f9fa;
  }
  
  .error-mensaje {
    background-color: #f8d7da;
    color: #721c24;
    border-color: #f5c6cb;
  }
  
  .sin-datos, .sin-resultados {
    background-color: #f8f9fa;
    color: #6c757d;
  }
  
  .cargando-item, .error-item {
    padding: 10px;
    margin: 5px 0;
    font-size: 0.9rem;
  }
  
  .cargando-item {
    color: #6c757d;
  }
  
  .error-item {
    color: #721c24;
  }
  
  .descripcion-item {
    padding: 5px 0;
    border-bottom: 1px dotted #eee;
  }
  
  .descripcion-item:last-child {
    border-bottom: none;
  }
  
  /* Responsive */
  @media (max-width: 768px) {
    .botones-busqueda {
      flex-direction: column;
    }
    
    .boton-filtro {
      width: 100%;
    }
  }
  /* Estilos para los resultados directos */
.resultados-directos {
  margin-bottom: 20px;
  padding: 10px;
  border: 1px solid #ddd;
  border-radius: 5px;
  background-color: #f9f9f9;
}

.resultados-directos h3 {
  margin-bottom: 10px;
  color: #333;
  font-size: 16px;
}

.tipo-item-directo, .descripcion-item-directo {
  margin-bottom: 10px;
  border: 1px solid #eee;
  border-radius: 4px;
  background-color: white;
}

.info-container {
  padding: 8px 12px;
  font-size: 14px;
  color: #666;
}
</style>