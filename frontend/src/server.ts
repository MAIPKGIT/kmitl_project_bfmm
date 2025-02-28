// ---- โค้ดเดิมของอั๋น ----
// import {
//   AngularNodeAppEngine,
//   createNodeRequestHandler,
//   isMainModule,
//   writeResponseToNodeResponse,
// } from '@angular/ssr/node';
// import express from 'express';
// import { dirname, resolve } from 'node:path';
// import { fileURLToPath } from 'node:url';
// import * as fs from 'node:fs';
// import * as https from 'node:https';

// const serverDistFolder = dirname(fileURLToPath(import.meta.url));
// const browserDistFolder = resolve(serverDistFolder, '../browser');

// const app = express();
// const angularApp = new AngularNodeAppEngine();

// // Your REST API endpoints can go here
// // app.get('/api/**', (req, res) => { ... });

// app.use(
//   express.static(browserDistFolder, {
//     maxAge: '1y',
//     index: false,
//     redirect: false,
//   }),
// );

// app.use('/**', (req, res, next) => {
//   angularApp
//     .handle(req)
//     .then((response) =>
//       response ? writeResponseToNodeResponse(response, res) : next(),
//     )
//     .catch(next);
// });

// if (isMainModule(import.meta.url)) {
//   const port = process.env['PORT'] || 4200;
  
//   // Check if we should run in HTTPS mode (for development)
//   if (process.env['USE_HTTPS'] === 'true') {
//     try {
//       // Path to SSL certificates relative to where the server will run
//       const sslOptions = {
//         key: fs.readFileSync('ssl/private.key'),
//         cert: fs.readFileSync('ssl/certificate.crt')
//       };
      
//       https.createServer(sslOptions, app).listen(port, () => {
//         console.log(`Node Express server listening on https://localhost:${port}`);
//       });
//     } catch (error) {
//       console.error('Error starting HTTPS server:', error);
//       console.log('Falling back to HTTP...');
//       app.listen(port, () => {
//         console.log(`Node Express server listening on http://localhost:${port}`);
//       });
//     }
//   } else {
//     // Standard HTTP server (for production behind reverse proxy)
//     app.listen(port, () => {
//       console.log(`Node Express server listening on http://localhost:${port}`);
//     });
//   }
// }

// export const reqHandler = createNodeRequestHandler(app);

// ---- โค้ดของมายชั่วคราว ----
import {
  AngularNodeAppEngine,
  createNodeRequestHandler,
  isMainModule,
  writeResponseToNodeResponse,
} from '@angular/ssr/node';
import express from 'express';
import { dirname, resolve } from 'node:path';
import { fileURLToPath } from 'node:url';

const serverDistFolder = dirname(fileURLToPath(import.meta.url));
const browserDistFolder = resolve(serverDistFolder, '../browser');

const app = express();
const angularApp = new AngularNodeAppEngine();

/**
 * Example Express Rest API endpoints can be defined here.
 * Uncomment and define endpoints as necessary.
 *
 * Example:
 * ```ts
 * app.get('/api/**', (req, res) => {
 *   // Handle API request
 * });
 * ```
 */

/**
 * Serve static files from /browser
 */
app.use(
  express.static(browserDistFolder, {
    maxAge: '1y',
    index: false,
    redirect: false,
  }),
);

/**
 * Handle all other requests by rendering the Angular application.
 */
app.use('/**', (req, res, next) => {
  angularApp
    .handle(req)
    .then((response) =>
      response ? writeResponseToNodeResponse(response, res) : next(),
    )
    .catch(next);
});

/**
 * Start the server if this module is the main entry point.
 * The server listens on the port defined by the `PORT` environment variable, or defaults to 4000.
 */
if (isMainModule(import.meta.url)) {
  const port = process.env['PORT'] || 4000;
  app.listen(port, () => {
    console.log(`Node Express server listening on http://localhost:${port}`);
  });
}

/**
 * The request handler used by the Angular CLI (dev-server and during build).
 */
export const reqHandler = createNodeRequestHandler(app);
