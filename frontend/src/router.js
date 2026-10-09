import { createRouter, createWebHistory } from 'vue-router';

// Páginas
import Login from './components/LogIn.vue';
import Register from './components/Register.vue';
import EmpleadoForm from './components/EmpleadoForm.vue';
import ProveedorForm from './components/ProveedorForm.vue';
import ClienteForm from './components/ClienteForm.vue';
import OrdenesForm from './components/OrdenesForm.vue';
import IntervencionForm from './components/IntervencionForm.vue';
import IntervencionOperario from './components/IntervencionOperario.vue';
import ComprasForm from './components/ComprasForm.vue';
import ConfiguracionesForm from './components/ConfiguracionesForm.vue';
import VerEmpleados from './components/VerEmpleados.vue';
import VerClientes from './components/VerClientes.vue';
import VerProveedores from './components/VerProveedores.vue';
import ConsultaIntervenciones from './components/ConsultaIntervenciones.vue';
import ConsultaCostosPorOrden from './components/ConsultaCostosPorOrden.vue';
import ClasificacionOrdenesForm from './components/ClasificacionOrdenesForm.vue';
import MenuPage from './components/MenuPage.vue';
import CambiarContrasena from './components/CambiarContrasena.vue';
import EditarRoles from './components/EditarRoles.vue';
import VerOrdenes from './components/VerOrdenes.vue';
import ServiciosForm from './components/ServiciosForm.vue';
import VerStock from './components/VerStock.vue';
import VerClasificacionOrdenes from './components/VerClasificacionOrdenes.vue';
import VerServicios from './components/VerServicios.vue';
import HomePage from './components/HomePage.vue';
import IntervencionesTodas from './components/IntervencionesTodas.vue';

// Store de sesión
import { getCurrentUser, setCurrentUser } from '@/sessionStore';

const routes = [
  { path: '/', redirect: '/homePage' },

   // públicas
  { path: '/homePage', name: 'HomePage', component: HomePage },  
  { path: '/login', name: 'Login', component: Login },
  { path: '/register', name: 'Register', component: Register },

  // privadas
  { path: '/menu', name: 'MenuPage', component: MenuPage, meta: { requiresAuth: true, roles: ['admin', 'propietario'] } },
  { path: '/empleado-form', name: 'EmpleadoForm', component: EmpleadoForm, meta: { requiresAuth: true } },
  { path: '/proveedor-form', name: 'ProveedorForm', component: ProveedorForm, meta: { requiresAuth: true } },
  { path: '/cliente-form', name: 'ClienteForm', component: ClienteForm, meta: { requiresAuth: true } },
  { path: '/ordenes-form', name: 'OrdenesForm', component: OrdenesForm, meta: { requiresAuth: true } },
  { path: '/intervencion-form', name: 'IntervencionForm', component: IntervencionForm, meta: { requiresAuth: true } },

  // solo operario
  {
    path: '/intervencion-operario',
    name: 'IntervencionOperario',
    component: IntervencionOperario,
    meta: { requiresAuth: true, roles: ['operario'] },
  },

  { path: '/compras-form', name: 'ComprasForm', component: ComprasForm, meta: { requiresAuth: true } },
  { path: '/parametros-form', name: 'ConfiguracionesForm', component: ConfiguracionesForm, meta: { requiresAuth: true } },
  { path: '/ver-empleados', name: 'VerEmpleados', component: VerEmpleados, meta: { requiresAuth: true } },
  { path: '/ver-clientes', name: 'VerClientes', component: VerClientes, meta: { requiresAuth: true } },
  { path: '/ver-proveedores', name: 'VerProveedores', component: VerProveedores, meta: { requiresAuth: true } },
  { path: '/consulta-intervenciones', name: 'ConsultaIntervenciones', component: ConsultaIntervenciones, meta: { requiresAuth: true } },
  { path: '/consulta-costos-por-orden', name: 'ConsultaCostosPorOrden', component: ConsultaCostosPorOrden, meta: { requiresAuth: true } },
  { path: '/clasificacion-ordenes', name: 'ClasificacionOrdenes', component: ClasificacionOrdenesForm, meta: { requiresAuth: true } },
  { path: '/cambiar-contrasena', name: 'CambiarContrasena', component: CambiarContrasena, meta: { requiresAuth: true } },
  { path: '/editar-roles', name: 'EditarRoles', component: EditarRoles, meta: { requiresAuth: true } },
  { path: '/ver-ordenes', name: 'VerOrdenes', component: VerOrdenes, meta: { requiresAuth: true } },
  { path: '/servicios-form', name: 'ServiciosForm', component: ServiciosForm, meta: { requiresAuth: true } },
  { path: '/ver-stock', name: 'VerStock', component: VerStock, meta: { requiresAuth: true } },
  { path: '/ver-clasificacion-ordenes', name: 'VerClasificacionOrdenes', component: VerClasificacionOrdenes, meta: { requiresAuth: true } },
  { path: '/ver-servicios', name: 'VerServicios', component: VerServicios, meta: { requiresAuth: true } },
  { path: '/ver-intervenciones', name: 'IntervencionesTodas', component: IntervencionesTodas, meta: { requiresAuth: true } },
];

const router = createRouter({
  history: createWebHistory(),
  routes,
});

const PUBLIC_PATHS = new Set(['/login', '/register', '/homePage']);

// Reconstruir usuario desde localStorage (modo dev)
function getUserFromLocalStorage() {
  try {
    const usuario = localStorage.getItem('usuario');
    const rol = (localStorage.getItem('rol') || '').trim().toLowerCase();
    const cedula = localStorage.getItem('cedula') || '';
    if (usuario && rol) return { usuario, rol, cedula };
  } catch {}
  return null;
}

function homeByRole(rol) {
  if (rol === 'operario') return '/intervencion-operario';
  if (rol === 'admin' || rol === 'propietario') return '/menu';
  return '/login';
}

// ✅ ÚNICO guard (estable)
router.beforeEach((to, from) => {
  // Debug útil (y seguro)
  if (to.path === '/login') {
    console.trace('🚨 Navegación a /login desde:', from.fullPath);
  }

  // Públicas
  if (PUBLIC_PATHS.has(to.path)) {
    // Si ya está logueado y quiere ir a login, mandarlo a su home
    const existing = getCurrentUser() || getUserFromLocalStorage();
    if (to.path === '/login' && existing?.rol) {
      return { path: homeByRole(existing.rol) };
    }
    return true;
  }

  // Solo protegemos si la ruta pide auth
  const requiresAuth = to.matched.some(r => r.meta?.requiresAuth);
  if (!requiresAuth) return true;

  // Usuario desde store o localStorage
  let user = getCurrentUser();
  if (!user) {
    user = getUserFromLocalStorage();
    if (user) setCurrentUser(user);
  }

  if (!user) {
    return { path: '/login' };
  }

  const rol = (user.rol || '').toLowerCase();

  // Si la ruta declara roles permitidos, respetar
  const allowedRoles = to.meta?.roles;
  if (Array.isArray(allowedRoles) && !allowedRoles.includes(rol)) {
    return { path: homeByRole(rol) };
  }

  // Regla extra: operario restringido a ciertas rutas
  if (
    rol === 'operario' &&
    !['/intervencion-operario', '/ordenes-form', '/cambiar-contrasena'].includes(to.path)
  ) {
    return { path: '/intervencion-operario' };
  }

  return true;
});

export default router;
