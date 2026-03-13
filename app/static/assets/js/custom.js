/* ==========================================================================
   Custom Scripts — Real Estate Demographics
   Shared across index.html and predictions.html
   ========================================================================== */

(function () {
	'use strict';

	var backToTopBtn = document.getElementById('back-to-top');
	var themeToggle = document.getElementById('theme-toggle');
	var headerEl = document.getElementById('header');

	/* Header scroll effect --------------------------------------------------*/
	function onScroll() {
		var scrolled = window.scrollY > 60;
		if (headerEl) {
			headerEl.classList.toggle('header-scrolled', scrolled);
		}
		if (backToTopBtn) {
			backToTopBtn.classList.toggle('visible', window.scrollY > 300);
		}
	}
	window.addEventListener('scroll', onScroll);
	onScroll();

	/* Back to Top -----------------------------------------------------------*/
	if (backToTopBtn) {

		backToTopBtn.addEventListener('click', function () {
			window.scrollTo({ top: 0, behavior: 'smooth' });
		});

		backToTopBtn.addEventListener('keydown', function (e) {
			if (e.key === 'Enter' || e.key === ' ') {
				e.preventDefault();
				window.scrollTo({ top: 0, behavior: 'smooth' });
			}
		});
	}

	/* Theme Toggle ----------------------------------------------------------*/
	if (themeToggle) {
		if (localStorage.getItem('theme') === 'light') {
			document.body.classList.add('light-mode');
			themeToggle.textContent = '\u{1F319}';
		}

		themeToggle.addEventListener('click', function () {
			document.body.classList.toggle('light-mode');
			var isLight = document.body.classList.contains('light-mode');
			themeToggle.textContent = isLight ? '\u{1F319}' : '\u{1F313}';
			localStorage.setItem('theme', isLight ? 'light' : 'dark');
		});
	}

	/* Lazy Load Charts with Intersection Observer ---------------------------*/
	var chartCards = document.querySelectorAll('.chart-card');
	if (chartCards.length > 0 && 'IntersectionObserver' in window) {
		var observer = new IntersectionObserver(
			function (entries) {
				entries.forEach(function (entry) {
					if (entry.isIntersecting) {
						entry.target.classList.add('loaded');
						observer.unobserve(entry.target);
					}
				});
			},
			{ rootMargin: '50px', threshold: 0.1 }
		);

		chartCards.forEach(function (card) {
			card.classList.add('lazy-chart');
			observer.observe(card);
		});
	}

	/* Plotly Responsive Resize ----------------------------------------------*/
	window.addEventListener('resize', function () {
		var plots = document.querySelectorAll('.js-plotly-plot');
		plots.forEach(function (plot) {
			if (window.Plotly) {
				window.Plotly.Plots.resize(plot);
			}
		});
	});

	/* State Selector Search Filter ------------------------------------------*/
	var searchInput = document.getElementById('state-search');
	var stateSelect = document.getElementById('state-select');

	if (searchInput && stateSelect) {
		searchInput.addEventListener('input', function () {
			var filter = this.value.toLowerCase();
			var options = stateSelect.options;
			for (var i = 0; i < options.length; i++) {
				var text = options[i].text.toLowerCase();
				options[i].style.display = text.indexOf(filter) !== -1 ? '' : 'none';
			}
		});

		searchInput.addEventListener('keydown', function (e) {
			if (e.key === 'Enter') {
				e.preventDefault();
				var options = stateSelect.options;
				for (var i = 0; i < options.length; i++) {
					if (options[i].style.display !== 'none') {
						window.location.href = '/state?state=' + options[i].value;
						return;
					}
				}
			}
		});

		stateSelect.addEventListener('change', function () {
			var abbr = this.value;
			if (abbr) {
				window.location.href = '/state?state=' + abbr;
			}
		});
	}
})();
