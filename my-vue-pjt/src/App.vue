<template>
  <header>
    <nav class="navbar navbar-expand navbar-dark bg-dark sticky-top shadow-sm">
      <div class="container">
        <RouterLink class="navbar-brand fw-bold" :to="{ name: 'home' }">🎬 MovieFlix</RouterLink>
        <ul class="navbar-nav gap-1 flex-wrap">
          <li class="nav-item">
            <RouterLink class="nav-link" :to="{ name: 'home' }" exact-active-class="active">Home</RouterLink>
          </li>
          <li class="nav-item">
            <RouterLink class="nav-link" :to="{ name: 'movies' }" active-class="active">Movies</RouterLink>
          </li>
          <li class="nav-item">
            <RouterLink class="nav-link" :to="{ name: 'reviewSearch' }" active-class="active">Review Search</RouterLink>
          </li>
          <li class="nav-item">
            <RouterLink class="nav-link" :to="{ name: 'recommended' }" active-class="active">Recommended</RouterLink>
          </li>
        </ul>
      </div>
    </nav>
  </header>

  <main class="container py-4">
    <RouterView />
  </main>
</template>

<script setup>
import { RouterLink, RouterView } from 'vue-router'
</script>
