// export default {
//   server: {
//     port: 3000,
//     strictPort: true,
//   },
//
//   resolve: {
//     alias: {
//       '@': '/src',
//     }
//   }
// };


import { defineConfig } from 'vite';

export default defineConfig({
  server: {
    port: 3000,
    strictPort: true,
  },

  resolve: {
    alias: {
      '@': '/src',
    }
  },

  // build: {
  //   rollupOptions: {
  //     input: {
  //       main: './vite/src/main.js',
  //       // about: './src/about.js'
  //     }
  //   }
  // }
});
