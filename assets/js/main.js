document.addEventListener('DOMContentLoaded', ready, false);

const THEME_PREF_STORAGE_KEY = "theme-preference";
const THEME_TO_ICON_CLASS = {
    'dark': 'feather-moon',
    'light': 'feather-sun'
};
const THEME_TO_ICON_TEXT_CLASS = {
    'dark': 'Dark mode',
    'light': 'Light mode'
};

const HEADING_TO_TOC_CLASS = {
    'H1': 'level-1',
    'H2': 'level-2',
    'H3': 'level-3',
    'H4': 'level-4'
}

function ready() {
    feather.replace({ 'stroke-width': 1, width: 20, height: 20 });
    setThemeByUserPref();

    const postContainer = document.querySelector('main#content > .container.post');
    if (postContainer !== null && document.getElementById('TableOfContents') !== null) {
        fixTocItemsIndent();
        createScrollSpy();
    }

    // Elements to inject
    const svgsToInject = document.querySelectorAll('img.svg-inject');
    // Do the injection
    SVGInjector(svgsToInject);

    const observer = new MutationObserver(() => {
        normalizeSvgPaths();
    });

    observer.observe(document.body, { childList: true, subtree: true });

    function normalizeSvgPaths() {
        document.querySelectorAll('.nav-link a .svg-inject').forEach(path => {
            const bbox = path.getBBox();
            const scaleX = 20 / bbox.width;
            const scaleY = 20 / bbox.height;
            const scale = Math.min(scaleX, scaleY);

            path.setAttribute('transform', `scale(${scale}) translate(${-bbox.x}, ${-bbox.y})`);
            path.setAttribute('stroke', 'currentColor');
            path.setAttribute('stroke-width', '1');
            path.setAttribute('fill', 'transparent');
        });
    }

    document.getElementById('hamburger-menu-toggle').addEventListener('click', () => {
        const hamburgerMenu = document.getElementsByClassName('nav-hamburger-list')[0]
        const hamburgerMenuToggleTarget = document.getElementById("hamburger-menu-toggle-target")
        if (hamburgerMenu.classList.contains('visibility-hidden')) {
            hamburgerMenu.classList.remove('visibility-hidden');
            hamburgerMenuToggleTarget.setAttribute("aria-checked", "true");
        } else {
            hamburgerMenu.classList.add('visibility-hidden');
            hamburgerMenuToggleTarget.setAttribute("aria-checked", "false");
        }
    })
}

window.addEventListener('scroll', () => {
    if (window.innerWidth <= 820) {
        // For smaller screen, show shadow earlier
        toggleHeaderShadow(50);
    } else {
        toggleHeaderShadow(100);
    }
});

function fixTocItemsIndent() {
    document.querySelectorAll('#TableOfContents a').forEach($tocItem => {
        const itemId = $tocItem.getAttribute("href").substring(1)
        $tocItem.classList.add(HEADING_TO_TOC_CLASS[document.getElementById(itemId).tagName]);
    });
}

function createScrollSpy() {
    var elements = document.querySelectorAll('#toc a');
    document.addEventListener('scroll', function() {
        elements.forEach(function(element) {
            const boundingRect = document.getElementById(element.getAttribute('href').substring(1)).getBoundingClientRect();
            if (boundingRect.top <= 55 && boundingRect.bottom >= 0) {
                elements.forEach(function(elem) {
                    elem.classList.remove('active');
                });
                element.classList.add('active');
            }
        });
    });
}

function toggleHeaderShadow(scrollY) {
    if (window.scrollY > scrollY) {
        document.querySelectorAll('.header').forEach(function(item) {
            item.classList.add('header-shadow')
        })
    } else {
        document.querySelectorAll('.header').forEach(function(item) {
            item.classList.remove('header-shadow')
        })
    }
}

function getPreferredTheme() {
    const initialTheme = document.documentElement.dataset.theme;
    if (initialTheme === 'dark' || initialTheme === 'light') {
        return initialTheme;
    }

    try {
        const storedTheme = localStorage.getItem(THEME_PREF_STORAGE_KEY);
        if (storedTheme === 'dark' || storedTheme === 'light') {
            return storedTheme;
        }
    } catch (_) {
        // Fall back to the operating-system preference when storage is unavailable.
    }

    return window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light';
}

function setThemeByUserPref() {
    const darkThemeToggles = document.querySelectorAll('.dark-theme-toggle');
    setTheme(getPreferredTheme(), darkThemeToggles);
    darkThemeToggles.forEach(el => el.addEventListener('click', toggleTheme, { capture: true }));
}

function toggleTheme() {
    const currentTheme = document.documentElement.dataset.theme;
    const themeToSet = currentTheme === 'dark' ? 'light' : 'dark';
    setThemeAndStore(themeToSet, document.querySelectorAll('.dark-theme-toggle'));
}

function setTheme(themeToSet, targets) {
    document.documentElement.dataset.theme = themeToSet;
    targets.forEach((target) => {
        target.querySelector('a').innerHTML = feather.icons[THEME_TO_ICON_CLASS[themeToSet].split('-')[1]].toSvg();
        target.querySelector(".dark-theme-toggle-screen-reader-target").textContent = THEME_TO_ICON_TEXT_CLASS[themeToSet];
    });
}

function setThemeAndStore(themeToSet, targets) {
    setTheme(themeToSet, targets);

    try {
        localStorage.setItem(THEME_PREF_STORAGE_KEY, themeToSet);
    } catch (_) {
        // The active page still changes theme even when storage is unavailable.
    }
}
