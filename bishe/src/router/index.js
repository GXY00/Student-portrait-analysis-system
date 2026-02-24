import Vue from 'vue'
import Router from 'vue-router'
import Login from '@/components/Login'
import ForgotPassword from '@/components/ForgotPassword'
import Home from '@/components/Home'

Vue.use(Router)

export default new Router({
  routes: [
    {
      path: '/',
      name: 'Login',
      component: Login
    },
    {
      path: '/forgot-password',
      name: 'ForgotPassword',
      component: ForgotPassword
    },
    {
      path: '/home',
      name: 'Home',
      component: Home
    }
  ]
})
