// Edit this value later if you want a different domain
let domain = '127.0.0.1:8000';

const endpoints = [
    { path: '/', method: 'GET', description: 'Home endpoint' },
    { path: '/viewData/', method: 'GET', description: 'View single data entry' },
    { path: '/viewAllData/', method: 'GET', description: 'View all data entries' },
    { path: '/backupData/', method: 'GET', description: 'Backup all data' },
    { path: '/deactivateAccount/', method: 'POST', description: 'Deactivate user account' },
    { path: '/deleteAllData/', method: 'DELETE', description: 'Delete all user data' },
    { path: '/updatePassword/', method: 'PUT', description: 'Update user password' },
    { path: '/updateEmail/', method: 'PUT', description: 'Update user email' },
    { path: '/updateUsername/', method: 'PUT', description: 'Update user username' },
];

const methodClass = method => `method-${method.toLowerCase()}`;

function renderEndpoints() {
    const list = document.getElementById('endpoint-list');
    list.innerHTML = '';
    endpoints.forEach((endpoint, index) => {
        const card = document.createElement('button');
        card.className = 'endpoint-card';
        card.type = 'button';
        card.innerHTML = `
            <div>
                <h2>${endpoint.path}</h2>
                <p>${endpoint.description}</p>
            </div>
            <div class="endpoint-footer">
                <span class="endpoint-label ${methodClass(endpoint.method)}">${endpoint.method}</span>
                <span class="endpoint-action">Open</span>
            </div>
        `;
        card.addEventListener('click', () => openEndpoint(endpoint));
        card.style.animationDelay = `${index * 45}ms`;
        list.appendChild(card);
    });
}

function openEndpoint(endpoint) {
    const url = `http://${domain}${endpoint.path}`;
    window.location.href = url;
}

function updateDomain() {
    const input = document.getElementById('domain-input');
    domain = input.value.trim() || domain;
    document.getElementById('domain-text').textContent = domain;
}

function setupForm() {
    const saveButton = document.getElementById('save-domain');
    const domainInput = document.getElementById('domain-input');
    saveButton.addEventListener('click', updateDomain);
    domainInput.addEventListener('keydown', event => {
        if (event.key === 'Enter') {
            event.preventDefault();
            updateDomain();
        }
    });
}

function initPage() {
    document.getElementById('endpoint-count').textContent = endpoints.length;
    document.getElementById('domain-text').textContent = domain;
    renderEndpoints();
    setupForm();
}

document.addEventListener('DOMContentLoaded', initPage);
