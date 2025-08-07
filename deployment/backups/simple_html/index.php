<?php
/**
 * Ultra-Simple Static HTML Router
 * Serves HTML pages and maps asset URLs cleanly
 */

class UltraSimpleRouter {
    private $contentDir = 'simple_html';
    
    public function handleRequest() {
        // Get requested path
        $path = $_SERVER['REQUEST_URI'] ?? '/';
        $path = strtok($path, '?'); // Remove query string
        $path = trim($path, '/');
        
        // Security: prevent directory traversal
        if (strpos($path, '..') !== false || strpos($path, './') !== false) {
            $this->serve403();
            return;
        }
        
        // Handle asset requests: /assets/* → /simple_html/assets/*
        if (strpos($path, 'assets/') === 0) {
            $this->serveAsset($path);
            return;
        }
        
        // Handle page requests
        $this->servePage($path);
    }
    
    private function servePage($path) {
        // Default to index for empty path
        if (empty($path)) {
            $path = 'index';
        }
        
        // Based on the directory structure shown in id_part4, HTML files are in simple_html/pages/
        $htmlFile = "{$this->contentDir}/pages/{$path}.html";
        
        // Check if HTML file exists
        if (!file_exists($htmlFile)) {
            $this->serve404();
            return;
        }
        
        // Read and serve HTML content (no auto-injection)
        $htmlContent = file_get_contents($htmlFile);
        
        // Set headers and serve
        header('Content-Type: text/html; charset=UTF-8');
        echo $htmlContent;
    }
    
    private function serveAsset($assetPath) {
        // Map /assets/* to /simple_html/assets/*
        $fullPath = $this->contentDir . '/' . $assetPath;
        
        // Check if asset file exists
        if (!file_exists($fullPath)) {
            $this->serve404();
            return;
        }
        
        // Determine content type
        $extension = strtolower(pathinfo($fullPath, PATHINFO_EXTENSION));
        $contentType = $this->getContentType($extension);
        
        // Set appropriate headers
        header('Content-Type: ' . $contentType);
        
        // Serve the file
        readfile($fullPath);
    }
    
    private function getContentType($extension) {
        $mimeTypes = [
            'css' => 'text/css',
            'js' => 'application/javascript',
            'png' => 'image/png',
            'jpg' => 'image/jpeg',
            'jpeg' => 'image/jpeg',
            'gif' => 'image/gif',
            'svg' => 'image/svg+xml',
            'ico' => 'image/x-icon',
            'woff' => 'font/woff',
            'woff2' => 'font/woff2',
            'ttf' => 'font/ttf',
            'eot' => 'application/vnd.ms-fontobject'
        ];
        
        return $mimeTypes[$extension] ?? 'application/octet-stream';
    }
    
    private function serve404() {
        http_response_code(404);
        if (file_exists('templates/404.html')) {
            include 'templates/404.html';
        } else {
            echo '<h1>404 - Page Not Found</h1><p>The requested page could not be found.</p>';
        }
    }
    
    private function serve403() {
        http_response_code(403);
        echo '<h1>403 - Access Denied</h1><p>Access to this resource is forbidden.</p>';
    }
}

// Initialize and handle request
$router = new UltraSimpleRouter();
$router->handleRequest();
?> 