const CACHE_NAME = 'darkhostho-v3';
const STATIC_ASSETS = [
    'https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/css/bootstrap.min.css',
    'https://cdn.jsdelivr.net/npm/bootstrap-icons@1.11.1/font/bootstrap-icons.css',
    'https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/js/bootstrap.bundle.min.js',
    'https://unpkg.com/leaflet@1.9.4/dist/leaflet.css',
    'https://unpkg.com/leaflet@1.9.4/dist/leaflet.js'
];

self.addEventListener('install', function(event) {
    self.skipWaiting();
    event.waitUntil(
        caches.open(CACHE_NAME)
            .then(function(cache) {
                return cache.addAll(STATIC_ASSETS);
            })
            .catch(function(err) {
                console.log('Cache install failed:', err);
            })
    );
});

self.addEventListener('activate', function(event) {
    event.waitUntil(
        caches.keys().then(function(cacheNames) {
            return Promise.all(
                cacheNames.filter(function(cacheName) {
                    return cacheName !== CACHE_NAME;
                }).map(function(cacheName) {
                    return caches.delete(cacheName);
                })
            );
        }).then(function() {
            return self.clients.claim();
        })
    );
});

self.addEventListener('fetch', function(event) {
    const url = new URL(event.request.url);
    
    if (url.origin !== location.origin) {
        event.respondWith(
            caches.match(event.request).then(function(cached) {
                return cached || fetch(event.request);
            })
        );
        return;
    }
    
    event.respondWith(
        fetch(event.request)
            .then(function(response) {
                return response;
            })
            .catch(function() {
                return caches.match(event.request);
            })
    );
});
