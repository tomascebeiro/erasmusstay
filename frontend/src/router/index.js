import { createRouter, createWebHistory } from "vue-router";
import { useAuth } from "../composables/useAuth";

// Importaciones de todos los componentes y vistas
import ListadoAnuncios from "../components/ListadoAnuncios.vue";
import AnuncioDetalle from "../views/AnuncioDetalle.vue";
import Contacto from "../views/Contacto.vue";
import Login from "../views/Login.vue";
import Register from "../views/Register.vue";
import CrearAnuncio from "../views/CrearAnuncio.vue";
import AdminPanel from "../views/AdminPanel.vue";
import Inicio from "../views/Inicio.vue";
import Profile from "../views/Profile.vue";
const routes = [
  {
    path: "/",
    name: "inicio",
    component: Inicio,
  },
  {
    path: "/anuncios",
    name: "anuncios",
    component: ListadoAnuncios,
  },
  {
    path: "/anuncio/:id",
    name: "anuncio-detalle",
    component: AnuncioDetalle,
  },
  {
    path: "/crear-anuncio",
    name: "crear-anuncio",
    component: CrearAnuncio,
    meta: {
      requiresAuth: true,
    },
  },
  {
    path: "/contacto",
    name: "contacto",
    component: Contacto,
  },
  {
    path: "/login",
    name: "login",
    component: Login,
    meta: {
      guestOnly: true,
    },
  },
  { path: "/profile", name: "profile", component: Profile, meta: { requiresAuth: true } },
  {
    path: "/register",
    name: "register",
    component: Register,
    meta: {
      guestOnly: true,
    },
  },
  {
    path: "/admin-panel",
    name: "admin-panel",
    component: AdminPanel,
    meta: {
      requiresAuth: true,
      requiresAdmin: true,
    },
  }
];

const router = createRouter({
  history: createWebHistory(),
  routes,
});

export default router;

// Guardia global de seguridad del sistema
router.beforeEach(async (to) => {
  const { isAuthenticated, restoreSession, user } = useAuth();

  // 1. Restaurar sesión si hay un token en almacenamiento local
  if (!isAuthenticated.value && localStorage.getItem("token")) {
    await restoreSession();
  }

  // 2. Control de acceso para rutas que requieren autenticación general
  if (to.meta.requiresAuth && !isAuthenticated.value) {
    return "/login";
  }

  // 3. Control de acceso estricto para el Panel de Administración (Soporta rol o nombre 'admin')
  if (to.meta.requiresAdmin) {
    const esAdmin = user.value?.rol === 'administrador' || user.value?.username === 'admin';
    if (!esAdmin) {
      return "/";
    }
  }

  // 4. Evitar que usuarios logueados entren a Login o Registro
  if (to.meta.guestOnly && isAuthenticated.value) {
    return "/";
  }

  return true;
});