// Bookmarklet: drag this to your bookmarks bar, then click it on any page
// to quickly bookmark an image to the social site.
(function() {
  if (window.__bookmark_loaded) return;
  window.__bookmark_loaded = true;

  var siteUrl = 'http://127.0.0.1:8000/';

  // Collect images on the page
  var images = Array.from(document.querySelectorAll('img'))
    .filter(img => img.naturalWidth > 100 && img.naturalHeight > 100);

  if (!images.length) { alert('No images found on this page.'); return; }

  // Build a simple picker
  var overlay = document.createElement('div');
  overlay.style = 'position:fixed;top:0;left:0;width:100%;height:100%;background:rgba(0,0,0,0.7);z-index:99999;overflow:auto;';
  var close = document.createElement('button');
  close.textContent = 'Close';
  close.style = 'position:fixed;top:10px;right:10px;z-index:100000;';
  close.onclick = function() { document.body.removeChild(overlay); window.__bookmark_loaded = false; };
  overlay.appendChild(close);

  images.forEach(function(img) {
    var wrapper = document.createElement('div');
    wrapper.style = 'display:inline-block;margin:10px;cursor:pointer;background:#fff;padding:5px;';
    var thumbnail = document.createElement('img');
    thumbnail.src = img.src;
    thumbnail.style = 'max-width:150px;max-height:150px;display:block;';
    wrapper.appendChild(thumbnail);
    wrapper.onclick = function() {
      var url = siteUrl + 'images/create/?url=' + encodeURIComponent(img.src) + '&title=' + encodeURIComponent(document.title);
      window.open(url, '_blank');
      document.body.removeChild(overlay);
      window.__bookmark_loaded = false;
    };
    overlay.appendChild(wrapper);
  });

  document.body.appendChild(overlay);
})();
