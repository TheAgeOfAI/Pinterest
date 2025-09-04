const q = document.getElementById('q');
const grid = document.getElementById('grid');
const count = document.getElementById('count');
const exts = ['.jpg', '.jpeg', '.png', '.gif', '.webp', '.bmp', '.svg'];

async function loadImages() {
  const res = await fetch('images/');
  const text = await res.text();
  const parser = new DOMParser();
  const doc = parser.parseFromString(text, 'text/html');
  const links = Array.from(doc.querySelectorAll('a'));
  
  const images = links
    .map(a => a.getAttribute('href'))
    .filter(href => exts.some(ext => href.toLowerCase().endsWith(ext)));
  
  // Build gallery items
  grid.innerHTML = images.map(img => {
    const fullPath = 'images/' + img;
    const fakeWidth = 600;  // Placeholder (replace with actual metadata if possible)
    const fakeHeight = 400;
    return `
      <figure class="item">
        <img loading="lazy" data-src="${fullPath}" alt="${img}" width="${fakeWidth}" height="${fakeHeight}">
      </figure>`;
  }).join('');
  
  enableLazyLoading();
  updateCount();
  enableFilter();
  enableLightbox(images);
}

function updateCount() {
  const items = Array.from(grid.querySelectorAll('.item'));
  const visible = items.filter(el => !el.classList.contains('hidden')).length;
  count.textContent = visible + ' image' + (visible === 1 ? '' : 's');
}

function enableFilter() {
  const items = Array.from(grid.querySelectorAll('.item'));
  q.addEventListener('input', (e) => {
    const term = e.target.value.trim().toLowerCase();
    items.forEach(el => {
      const img = el.querySelector('img');
      const name = img.getAttribute('data-src').split('/').pop().toLowerCase();
      if (!term || name.includes(term)) {
        el.classList.remove('hidden');
      } else {
        el.classList.add('hidden');
      }
    });
    updateCount();
  });
}

function enableLazyLoading() {
  const items = document.querySelectorAll('.item img');
  const observer = new IntersectionObserver(entries => {
    entries.forEach(entry => {
      if (entry.isIntersecting) {
        const img = entry.target;
        img.src = img.dataset.src;
        img.onload = () => img.parentElement.classList.add('loaded');
        observer.unobserve(img);
      }
    });
  }, { rootMargin: '100px' });
  
  items.forEach(img => observer.observe(img));
}

function enableLightbox(images) {
  const lightbox = document.getElementById('lightbox');
  const lightboxImg = document.getElementById('lightbox-img');
  const btnClose = lightbox.querySelector('.close');
  const btnPrev = lightbox.querySelector('.prev');
  const btnNext = lightbox.querySelector('.next');
  
  let currentIndex = 0;

  function showLightbox(index) {
    currentIndex = index;
    lightboxImg.src = 'images/' + images[currentIndex];
    lightbox.classList.add('show');
  }

  function hideLightbox() {
    lightbox.classList.remove('show');
  }

  grid.addEventListener('click', (e) => {
    if (e.target.tagName === 'IMG') {
      const src = e.target.dataset.src;
      currentIndex = images.findIndex(img => 'images/' + img === src);
      showLightbox(currentIndex);
    }
  });

  btnClose.addEventListener('click', hideLightbox);
  lightbox.addEventListener('click', (e) => {
    if (e.target === lightbox) hideLightbox();
  });

  btnPrev.addEventListener('click', () => {
    currentIndex = (currentIndex - 1 + images.length) % images.length;
    showLightbox(currentIndex);
  });

  btnNext.addEventListener('click', () => {
    currentIndex = (currentIndex + 1) % images.length;
    showLightbox(currentIndex);
  });

  document.addEventListener('keydown', (e) => {
    if (!lightbox.classList.contains('show')) return;
    if (e.key === 'Escape') hideLightbox();
    if (e.key === 'ArrowLeft') btnPrev.click();
    if (e.key === 'ArrowRight') btnNext.click();
  });
}

loadImages();
