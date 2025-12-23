// --- Configuration Globale de Chart.js ---
Chart.defaults.font.family = "Segoe UI, Tahoma, Geneva, Verdana, sans-serif";
Chart.defaults.font.size = 12;
Chart.defaults.color = "#6c757d";

// --- Palette de Couleurs pour l'Application ---
const chartColors = {
    primary: "#3B82F6", 
    success: "#10B981", 
    danger: "#EF4444",  
    warning: "#F59E0B", 
    info: "#0EA5E9",    
    light: "#F3F4F6",   
    dark: "#111827",    
    line: "#8ACC16",    
    orange: "#FFA500",  
    purple: "#800080",  
    teal: "#008080",    
    indigo: '#6366F1'   
};
const colorPalette = [
    chartColors.primary,
    chartColors.success,
    chartColors.danger,
    chartColors.warning,
    chartColors.info,
    chartColors.orange,
    chartColors.purple,
    chartColors.teal,
    chartColors.indigo
];

function getColors(data, color = chartColors.primary) {
    if (Array.isArray(color)) {
        return color;
    }
    return Array(data.length).fill(color);
}

/**
 * DÉFINITION DE LA TAILLE DU PAS D'AXE (STEP SIZE)
 * Calcule la taille du pas de graduation en fonction de la valeur maximale de l'axe.
 */
function getStepSize(max) {
    if (max <= 10) {
        return 1;
    }
    if (max <= 20) {
        return 2;
    }
    if (max <= 50) {
        return 5;
    }
    if (max <= 100) {
        return max > 80 ? 20 : 10; 
    }
    if (max <= 200) {
        return 20; 
    }
    if (max <= 500) {
        return 50; 
    }
    return 100;
}

/**
 * Calcule le minimum et le maximum des valeurs de données pour ajuster l'échelle de l'axe.
 * Plafonne le max à 100 si les données sont dans cette plage.
 */
function calculateMinMax(dataOrDatasets) {
    let allValues = [];
    if (dataOrDatasets.length > 0 && typeof dataOrDatasets[0] === 'number') {
        allValues = dataOrDatasets;
    } else if (dataOrDatasets.length > 0 && typeof dataOrDatasets[0] === 'object' && dataOrDatasets[0].data && Array.isArray(dataOrDatasets[0].data)) {
        dataOrDatasets.forEach(dataset => {
            allValues = allValues.concat(dataset.data);
        });
    }

    if (allValues.length === 0) {
        return { min: 0, max: 10 }; 
    }

    const maxVal = Math.max(...allValues);
    const padding = maxVal * 0.05 + 1;
    
    let finalMax = maxVal + padding;
    
    const step = getStepSize(finalMax);
    let roundedMax = Math.ceil(finalMax / step) * step;
    
    if (roundedMax > 100) {
        if (maxVal > 100) {
            const newStep = getStepSize(maxVal);
            roundedMax = Math.ceil(maxVal / newStep) * newStep;
        } else {
            roundedMax = 100;
        }
    } else if (roundedMax < maxVal) {
        roundedMax += step;
    }
    
    return { 
        min: 0, 
        max: roundedMax 
    };
}


// --- Fonctions de Création de Graphiques ---

/**
 * Crée un graphique à barres horizontal.
 */
function createHorizontalBarChart(canvaId, labels, data, color = chartColors.primary, dataLabel = "Score") {
    const ctx = document.getElementById(canvaId);
    if (!ctx) return null;

    const backgroundColors = getColors(data, color);
    const { min, max } = calculateMinMax(data);
    const stepSize = getStepSize(max);

    return new Chart(ctx, {
        type: 'bar',
        data: {
            labels: labels,
            datasets: [{
                label: dataLabel,
                data: data,
                backgroundColor: backgroundColors,
                borderRadius: 4,
                borderSkipped: false,
                barPercentage: 0.8,
                categoryPercentage: 0.8,
            }]
        },
        options: {
            responsive: true,
            indexAxis: 'y',
            scales: {
                x: {
                    beginAtZero: true,
                    min: min,
                    max: max,
                    title: {
                        display: true,
                        text: dataLabel,
                    },
                    grid: { display: false },
                    ticks: {
                        stepSize: stepSize,
                        callback: function(value) {
                            if (Number.isInteger(value)) {
                                return value;
                            }
                        },
                        precision: 0 
                    }
                },
                y: {
                    title: {
                        display: false,
                    },
                    grid: { display: false }
                }
            },
            plugins: {
                legend: {
                    display: false,
                }
            }
        }
    });
}

/**
 * Crée un graphique linéaire (pour l'évolution dans le temps).
 */
function createLineChart(canvaId, labels, datasets) {
    const ctx = document.getElementById(canvaId);
    if (!ctx) return null;

    const { min, max } = calculateMinMax(datasets);
    const stepSize = getStepSize(max);

    const chartDatasets = datasets.map((dataset, index) => {
        const color = dataset.color || chartColors.primary; // Utilisation d'une couleur par défaut
        
        return {
            label: dataset.label,
            data: dataset.data,
            borderColor: color,
            backgroundColor: color, 
            tension: 0.4, 
            fill: false,
            pointRadius: 4,
            pointHoverRadius: 6,
        };
    });

    return new Chart(ctx, {
        type: 'line',
        data: {
            labels: labels,
            datasets: chartDatasets,
        },
        options: {
            responsive: true,
            scales: {
                y: {
                    beginAtZero: false,
                    min: min,
                    max: max,
                    title: {
                        display: true,
                        text: 'Score',
                    },
                    grid: { display: false },
                    ticks: {
                        stepSize: stepSize,
                        callback: function(value) {
                            if (Number.isInteger(value)) {
                                return value;
                            }
                        },
                        precision: 0
                    }
                },
                x: {
                    title: {
                        display: true,
                        text: 'Année',
                    },
                    grid: { display: false },
                    ticks: {
                        callback: function(value) {
                             if (Number.isInteger(value)) {
                                return value;
                            }
                        },
                        precision: 0
                    }
                }
            },
            plugins: {
                legend: {
                    display: true,
                    position: 'top',
                }
            }
        }
    });
}

// NOTE: Les fonctions createVerticalBarChart, Groupedbarchart et createPieOrDoughnutChart ont été omises pour la concision, 
// mais doivent utiliser la même logique d'axe dynamique si elles sont utilisées ailleurs.

function createPieOrDoughnutChart(canvaId, labels, data, isDoughnut = true, dataLabel = "Répartition") {
    const ctx = document.getElementById(canvaId);
    if (!ctx) return null;

    // Utilisation de la palette pour les couleurs des secteurs
    const backgroundColors = labels.map((_, index) => colorPalette[index % colorPalette.length]);

    return new Chart(ctx, {
        type: isDoughnut ? 'doughnut' : 'pie', // Choix du type
        data: {
            labels: labels,
            datasets: [{
                label: dataLabel,
                data: data,
                backgroundColor: backgroundColors,
                hoverOffset: 8, // Décalage au survol
            }]
        },
        options: {
            responsive: true,
            plugins: {
                legend: {
                    display: true,
                    position: 'right', // Afficher la légende à droite
                },
                tooltip: {
                    callbacks: {
                        // Ajout du pourcentage dans l'infobulle
                        label: function(context) {
                            let label = context.label || '';
                            if (label) {
                                label += ': ';
                            }
                            // Calcul du pourcentage
                            const total = context.dataset.data.reduce((acc, value) => acc + value, 0);
                            const currentValue = context.raw;
                            const percentage = ((currentValue / total) * 100).toFixed(1) + '%';
                            return label + currentValue + ' (' + percentage + ')';
                        }
                    }
                }
            }
        }
    });
}

/**
 * Crée un graphique à barres groupées (Grouped Bar Chart).
 * **Ajuste l'échelle de l'axe Y (numérique) dynamiquement.**
 * @param {string} canvaId - L'ID de l'élément canvas.
 * @param {Array<string>} labels - Les étiquettes de l'axe X (catégories).
 * @param {Array<{label: string, data: Array<number>, color?: string}>} datasets - Tableau d'objets pour chaque série de données (chaque groupe).
 * @returns {Chart|null} L'instance du graphique Chart.js.
 */
function createGroupedBarChart(canvaId, labels, datasets) {
    const ctx = document.getElementById(canvaId);
    if (!ctx) return null;

    const { min, max } = calculateMinMax(datasets); // Calcul dynamique de min/max

    const chartDatasets = datasets.map((dataset, index) => {
        // Utilise la couleur spécifiée ou une couleur de la palette par défaut
        const color = dataset.color || colorPalette[index % colorPalette.length];
        return {
            label: dataset.label,
            data: dataset.data,
            backgroundColor: color,
            borderColor: color,
            borderWidth: 1,
            borderRadius: 4,
            barPercentage: 0.9,
            categoryPercentage: 0.8,
        };
    });

    return new Chart(ctx, {
        type: 'bar',
        data: {
            labels: labels,
            datasets: chartDatasets,
        },
        options: {
            responsive: true,
            maintainAspectRatio: true,
            scales: {
                x: {
                    // Pour le groupement, les barres ne sont pas empilées (par défaut)
                    grid: { display: false },
                    ticks: {
                        autoSkip: false,
                        maxRotation: 0,
                        minRotation: 0,
                        font: {
                            size: 11
                        }
                    }
                },
                y: {
                    beginAtZero: true,
                    min: min, // Utilise la valeur dynamique minimale (souvent 0)
                    max: max, // Utilise la valeur dynamique maximale
                    grid: { color: 'rgba(0,0,0,0.05)' }
                }
            },
            plugins: {
                legend: {
                    display: true,
                    position: 'top',
                    labels: { usePointStyle: true } // Utilise des petits points pour la légende
                }
            }
        }
    });
}

// Alias for backward compatibility
const Groupedbarchart = createGroupedBarChart;

/**
 * Crée un graphique en secteurs (pie chart).
 * @param {string} canvaId - L'ID de l'élément canvas.
 * @param {Array<string>} labels - Les étiquettes des secteurs.
 * @param {Array<number>} data - Les valeurs de chaque secteur.
 * @param {string} type - Type de graphique: 'pie' ou 'doughnut' (par défaut 'pie').
 * @param {string} dataLabel - Label pour le dataset.
 * @returns {Chart|null} L'instance du graphique Chart.js.
 */
function createPieChart(canvaId, labels, data, type = 'pie', dataLabel = "Répartition") {
    return createPieOrDoughnutChart(canvaId, labels, data, type === 'doughnut', dataLabel);
}

// === SCROLL TO TOP BUTTON (FONCTION COMMUNE) ===
/**
 * Initialise le bouton "Remonter en haut" de manière unifiée.
 * Affiche le bouton après 200px de scroll et permet un retour instantané en haut de page.
 * Compatible avec tous les navigateurs.
 */
document.addEventListener('DOMContentLoaded', function() {
    const scrollBtn = document.getElementById('scrollToTopBtn');
    
    if (!scrollBtn) return; // Si le bouton n'existe pas sur la page, ne rien faire
    
    // Afficher/masquer le bouton selon le scroll
    window.addEventListener('scroll', function() {
        const scrollThreshold = 200;
        if (document.body.scrollTop > scrollThreshold || document.documentElement.scrollTop > scrollThreshold) {
            scrollBtn.style.display = 'block';
        } else {
            scrollBtn.style.display = 'none';
        }
    });
    
    // Remonter en haut au clic - Compatible tous navigateurs
    scrollBtn.addEventListener('click', function() {
        document.body.scrollTop = 0; // Pour Safari
        document.documentElement.scrollTop = 0; // Pour Chrome, Firefox, IE et Opera
    });
});