
import React, { useEffect, useState } from "react";

const API_URL = "https://choosecloud-backend-dne6hsbmfxadfabz.indiasouthcentral-01.azurewebsites.net";

function App() {
        // Authentication state
    const [token, setToken] = useState(
        sessionStorage.getItem("choosecloud_token") || ""
    );

    const [currentUser, setCurrentUser] = useState(null);
    const [authMode, setAuthMode] = useState("login");
    const [authName, setAuthName] = useState("");
    const [authEmail, setAuthEmail] = useState("");
    const [authPassword, setAuthPassword] = useState("");
    const [authLoading, setAuthLoading] = useState(false);
    const [authError, setAuthError] = useState("");
    const [providers, setProviders] = useState([]);
    const [prices, setPrices] = useState([]);
    const computePrices = prices.filter(
    (price) => price.category === "Compute"
);
    const [estimates, setEstimates] = useState([]);
    
    const [hours, setHours] = useState("730");
    const [storageGb, setStorageGb] = useState("100");
const [storageEstimates, setStorageEstimates] = useState([]);
const [storageCalculating, setStorageCalculating] = useState(false);
const [storageError, setStorageError] = useState("");

const [databaseHours, setDatabaseHours] = useState("730");
const [databaseStorageGb, setDatabaseStorageGb] = useState("20");
const [databaseEstimates, setDatabaseEstimates] = useState([]);
const [databaseCalculating, setDatabaseCalculating] = useState(false);
const [databaseError, setDatabaseError] = useState("");
const [recommendation, setRecommendation] = useState(null);
const [recommendationLoading, setRecommendationLoading] = useState(false);
const [recommendationError, setRecommendationError] = useState("");

const [forecastHorizon, setForecastHorizon] = useState("5");
const [forecastResult, setForecastResult] = useState(null);
const [forecastLoading, setForecastLoading] = useState(false);
const [forecastError, setForecastError] = useState("");
const [cloudShiftSource, setCloudShiftSource] = useState(
    "Amazon Web Services"
);
const [cloudShiftTarget, setCloudShiftTarget] = useState(
    "Microsoft Azure"
);

const [cloudShiftInputs, setCloudShiftInputs] = useState({
    compute_hours: "730",
    storage_gb: "100",
    database_hours: "730",
    database_storage_gb: "20"
});

const [cloudShiftResult, setCloudShiftResult] = useState(null);
const [cloudShiftLoading, setCloudShiftLoading] = useState(false);
const [cloudShiftError, setCloudShiftError] = useState("");
const [history, setHistory] = useState(() => {
    try {
        return JSON.parse(
            localStorage.getItem("choosecloud_history") || "[]"
        );
    } catch {
        return [];
    }
});
const [recommendationInputs, setRecommendationInputs] = useState({
    compute_hours: "730",
    storage_gb: "100",
    database_hours: "730",
    database_storage_gb: "20"
});

    const [loading, setLoading] = useState(true);
    const [calculating, setCalculating] = useState(false);
    const [error, setError] = useState("");
    const [pricingError, setPricingError] = useState("");

    // Restore authenticated session when the page reloads
    useEffect(() => {
        async function verifySession() {
            const savedToken = sessionStorage.getItem(
                "choosecloud_token"
            );

            if (!savedToken) {
                return;
            }

            try {
                const response = await fetch(
                    `${API_URL}/api/auth/me`,
                    {
                        headers: {
                            Authorization: `Bearer ${savedToken}`
                        }
                    }
                );

                if (!response.ok) {
                    throw new Error("Session expired");
                }

                const userData = await response.json();

                setCurrentUser(userData);
                setToken(savedToken);

            } catch (error) {
                sessionStorage.removeItem("choosecloud_token");
                setToken("");
                setCurrentUser(null);
            }
        }

        verifySession();
    }, []);
    // Handle Login and Registration
    async function handleAuthSubmit(event) {
        event.preventDefault();

        setAuthLoading(true);
        setAuthError("");

        try {
            if (authMode === "register") {
                const registerResponse = await fetch(
                    `${API_URL}/api/auth/register`,
                    {
                        method: "POST",
                        headers: {
                            "Content-Type": "application/json"
                        },
                        body: JSON.stringify({
                            name: authName,
                            email: authEmail,
                            password: authPassword
                        })
                    }
                );

                const registerData = await registerResponse.json();

                if (!registerResponse.ok) {
                    throw new Error(
                        registerData.detail || "Registration failed."
                    );
                }
            }

            // Login (also performed after successful registration)
            const loginResponse = await fetch(
                `${API_URL}/api/auth/login`,
                {
                    method: "POST",
                    headers: {
                        "Content-Type": "application/json"
                    },
                    body: JSON.stringify({
                        email: authEmail,
                        password: authPassword
                    })
                }
            );

            const loginData = await loginResponse.json();

            if (!loginResponse.ok) {
                throw new Error(
                    loginData.detail || "Login failed."
                );
            }

            sessionStorage.setItem(
                "choosecloud_token",
                loginData.access_token
            );

            setToken(loginData.access_token);
            setCurrentUser(loginData.user);
            setAuthPassword("");
            setAuthError("");

        } catch (error) {
            setAuthError(error.message);
        } finally {
            setAuthLoading(false);
        }
    }
    function handleLogout() {
    sessionStorage.removeItem("choosecloud_token");

    setToken("");
    setCurrentUser(null);
    setAuthEmail("");
    setAuthPassword("");
    setAuthError("");
    setAuthMode("login");
}


    useEffect(() => {
        async function fetchDashboardData() {

    
            try {
                const [providerResponse, priceResponse] =
                    await Promise.all([
                        fetch(`${API_URL}/api/providers`),
                        fetch(`${API_URL}/api/prices`)
                    ]);

                if (!providerResponse.ok || !priceResponse.ok) {
                    throw new Error("Unable to fetch dashboard data.");
                }

                const providerData = await providerResponse.json();
                const priceData = await priceResponse.json();

                setProviders(providerData.providers);
                setPrices(priceData.prices);
                setError("");
            } catch (err) {
                setError(
                    "Cannot connect to ChooseCloud backend. Please check whether the API is running."
                );
            } finally {
                setLoading(false);
            }
        }

        fetchDashboardData();
    }, []);
    function saveHistory(entry) {
    setHistory((previousHistory) => {
        const updatedHistory = [
            {
                id: Date.now(),
                createdAt: new Date().toLocaleString(),
                ...entry
            },
            ...previousHistory
        ];

        localStorage.setItem(
            "choosecloud_history",
            JSON.stringify(updatedHistory)
        );

        return updatedHistory;
    });
}
    async function calculateCosts() {
        const quantity = Number(hours);

        if (!Number.isFinite(quantity) || quantity <= 0) {
            setPricingError("Please enter a valid number of hours.");
            return;
        }

       if (computePrices.length === 0) {
    setPricingError("No compute pricing records are available.");
    return;
}

        setCalculating(true);
        setPricingError("");
        setEstimates([]);

        try {
            const results = await Promise.all(
                computePrices.map(async (price) => {
                    const response = await fetch(
                        `${API_URL}/api/cost/estimate`,
                        {
                            method: "POST",
                            headers: {
                                "Content-Type": "application/json"
                            },
                            body: JSON.stringify({
                                price_id: price.price_id,
                                usage_quantity: quantity
                            })
                        }
                    );

                    if (!response.ok) {
                        throw new Error(
                            `Cost calculation failed for ${price.provider}.`
                        );
                    }

                    const estimate = await response.json();

                    return {
                        ...estimate,
                        provider: price.provider,
                        service: price.service,
                        configuration: price.configuration
                    };
                })
            );

            setEstimates(results);
            saveHistory({
    type: "Compute Cost Comparison",
    summary: `${results.length} compute pricing options compared`,
    details: results
});
        } catch (err) {
            setPricingError(err.message || "Unable to calculate costs.");
        } finally {
            setCalculating(false);
        }
    }

async function calculateStorageCosts() {
    const quantity = Number(storageGb);

    if (!Number.isFinite(quantity) || quantity <= 0) {
        setStorageError("Please enter a valid storage capacity.");
        return;
    }

    setStorageCalculating(true);
    setStorageError("");
    setStorageEstimates([]);

    try {
        const response = await fetch(
            `${API_URL}/api/storage/estimate`,
            {
                method: "POST",
                headers: {
                    "Content-Type": "application/json"
                },
                body: JSON.stringify({
                    storage_gb: quantity
                })
            }
        );

        if (!response.ok) {
            throw new Error("Storage calculation failed.");
        }

        const data = await response.json();

        setStorageEstimates(data.results);
        saveHistory({
    type: "Storage Cost Comparison",
    summary: `${data.results.length} storage pricing options compared`,
    details: data.results
});
    } catch (err) {
        setStorageError(
            err.message || "Unable to calculate storage costs."
        );
    } finally {
        setStorageCalculating(false);
    }
}

async function calculateDatabaseCosts() {
    const hours = Number(databaseHours);
    const storage = Number(databaseStorageGb);

    if (!Number.isFinite(hours) || hours <= 0 || hours > 744) {
        setDatabaseError("Enter valid usage hours between 1 and 744.");
        return;
    }

    if (!Number.isFinite(storage) || storage <= 0) {
        setDatabaseError("Enter a valid storage capacity.");
        return;
    }

    setDatabaseCalculating(true);
    setDatabaseError("");
    setDatabaseEstimates([]);

    try {
        const response = await fetch(
            `${API_URL}/api/database/estimate`,
            {
                method: "POST",
                headers: {
                    "Content-Type": "application/json"
                },
                body: JSON.stringify({
                    usage_hours: hours,
                    storage_gb: storage
                })
            }
        );

        if (!response.ok) {
            throw new Error("Database cost calculation failed.");
        }

        const data = await response.json();

        setDatabaseEstimates(data.results);
        saveHistory({
    type: "Database Cost Comparison",
    summary: `${data.results.length} database pricing options compared`,
    details: data.results
});
    } catch (err) {
        setDatabaseError(
            err.message || "Unable to calculate database costs."
        );
    } finally {
        setDatabaseCalculating(false);
    }
}
async function generateRecommendation() {
    setRecommendationLoading(true);
    setRecommendationError("");
    setRecommendation(null);

    try {
        const response = await fetch(
            `${API_URL}/api/recommend`,
            {
                method: "POST",
                headers: {
                    "Content-Type": "application/json"
                },
                body: JSON.stringify({
                    compute_hours: Number(
                        recommendationInputs.compute_hours
                    ),
                    storage_gb: Number(
                        recommendationInputs.storage_gb
                    ),
                    database_hours: Number(
                        recommendationInputs.database_hours
                    ),
                    database_storage_gb: Number(
                        recommendationInputs.database_storage_gb
                    )
                })
            }
        );

        if (!response.ok) {
            throw new Error("Recommendation request failed.");
        }

        const data = await response.json();

        setRecommendation(data);
        saveHistory({
    type: "Cloud Cost Recommendation",
    summary: "Multi-cloud cost recommendation generated",
    details: data
});

    } catch (error) {
        setRecommendationError(
            error.message || "Unable to generate recommendation."
        );
    } finally {
        setRecommendationLoading(false);
    }
}
async function generateCloudShiftAnalysis() {
    setCloudShiftLoading(true);
    setCloudShiftError("");
    setCloudShiftResult(null);

    try {
        const response = await fetch(
            `${API_URL}/api/cloudshift/analyze`,
            {
                method: "POST",
                headers: {
                    "Content-Type": "application/json"
                },
                body: JSON.stringify({
                    source_provider: cloudShiftSource,
                    target_provider: cloudShiftTarget,
                    compute_hours: Number(
                        cloudShiftInputs.compute_hours
                    ),
                    storage_gb: Number(
                        cloudShiftInputs.storage_gb
                    ),
                    database_hours: Number(
                        cloudShiftInputs.database_hours
                    ),
                    database_storage_gb: Number(
                        cloudShiftInputs.database_storage_gb
                    )
                })
            }
        );

        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(
                errorData.detail || "CloudShift analysis failed."
            );
        }

        const data = await response.json();
        setCloudShiftResult(data);
        saveHistory({
    type: "CloudShift Migration Analysis",
    summary: `${data.source_provider} → ${data.target_provider}`,
    details: data
});

    } catch (error) {
        setCloudShiftError(
            error.message || "Unable to analyze cloud migration."
        );
    } finally {
        setCloudShiftLoading(false);
    }
}

async function generateWorkloadForecast() {
    setForecastLoading(true);
    setForecastError("");
    setForecastResult(null);

    try {
        const observationsResponse = await fetch(
            `${API_URL}/api/workload/latest-observations`
        );

        if (!observationsResponse.ok) {
            throw new Error("Unable to load workload observations.");
        }

        const observationsData = await observationsResponse.json();

        const forecastResponse = await fetch(
            `${API_URL}/api/workload/forecast`,
            {
                method: "POST",
                headers: {
                    "Content-Type": "application/json"
                },
                body: JSON.stringify({
                    observations: observationsData.observations,
                    horizon_minutes: Number(forecastHorizon)
                })
            }
        );

        if (!forecastResponse.ok) {
            const errorData = await forecastResponse.json();
            throw new Error(
                errorData.detail || "Workload forecast failed."
            );
        }

        const result = await forecastResponse.json();
        setForecastResult(result);

    } catch (error) {
        setForecastError(
            error.message || "Unable to generate workload forecast."
        );
    } finally {
        setForecastLoading(false);
    }
}

    const cheapestCost =
        estimates.length > 0
            ? Math.min(...estimates.map(item => item.estimated_cost_inr))
            : null;

    const providerColors = {
        AWS: "#f59e0b",
        AZURE: "#38bdf8",
        GCP: "#34d399"
    };

    const formatINR = (amount) =>
        new Intl.NumberFormat("en-IN", {
            style: "currency",
            currency: "INR",
            maximumFractionDigits: 2
        }).format(amount);

   
    // Show Login / Registration when the user is not authenticated
    if (!token || !currentUser) {
        return (
            <div className="auth-page">
                <div className="auth-card">
                    <h1>ChooseCloud</h1>
                    <p>Intelligent Multi-Cloud Cost Platform</p>

                    <h2>
                        {authMode === "login"
                            ? "Welcome Back"
                            : "Create Your Account"}
                    </h2>

                    <form onSubmit={handleAuthSubmit}>
                        {authMode === "register" && (
                            <input
                                type="text"
                                placeholder="Full Name"
                                value={authName}
                                onChange={(e) =>
                                    setAuthName(e.target.value)
                                }
                                required
                            />
                        )}

                        <input
                            type="email"
                            placeholder="Email Address"
                            value={authEmail}
                            onChange={(e) =>
                                setAuthEmail(e.target.value)
                            }
                            required
                        />

                        <input
                            type="password"
                            placeholder="Password"
                            value={authPassword}
                            onChange={(e) =>
                                setAuthPassword(e.target.value)
                            }
                            minLength={8}
                            required
                        />

                        {authError && (
                            <p className="auth-error">
                                {authError}
                            </p>
                        )}

                        <button
                            type="submit"
                            disabled={authLoading}
                        >
                            {authLoading
                                ? "Please wait..."
                                : authMode === "login"
                                ? "Login"
                                : "Register"}
                        </button>
                    </form>

                    <p className="auth-switch">
                        {authMode === "login"
                            ? "Don't have an account?"
                            : "Already have an account?"}

                        <button
                            type="button"
                            onClick={() => {
                                setAuthMode(
                                    authMode === "login"
                                        ? "register"
                                        : "login"
                                );
                                setAuthError("");
                            }}
                        >
                            {authMode === "login"
                                ? "Register"
                                : "Login"}
                        </button>
                    </p>
                </div>
            </div>
        );
    }

    return (
        <div className="app">

            <aside className="sidebar">
                <div className="brand">
                    <span className="brand-icon">☁</span>
                    ChooseCloud
                </div>

                <p className="menu-label">MAIN MENU</p>

                <nav>
                    <a className="nav-link active" href="#dashboard">
                        <span>▦</span> Dashboard
                    </a>
                    <a className="nav-link" href="#providers">
                        <span>☁</span> Cloud Providers
                    </a>
                    <a className="nav-link" href="#pricing">
                        <span>₹</span> Cost Comparison
                    </a>
                    <a className="nav-link" href="#storage">
    <span>▤</span> Storage Comparison
</a>
<a className="nav-link" href="#database">
    <span>▣</span> Database Comparison
</a>
                    <a className="nav-link" href="#recommendations">
                        <span>✧</span> Recommendations
                    </a>
                    <a className="nav-link" href="#cloudshift">
                    <span className="nav-icon">⇄</span>
                     <span>CloudShift</span>
                    </a>
                    <a className="nav-link" href="#history">
                        <span>◷</span> History
                    </a>
                    
                </nav>
<div className="sidebar-footer">
    <div className="profile-avatar">
        {currentUser?.name?.charAt(0).toUpperCase() || "U"}
    </div>

    <div>
        <strong>{currentUser?.name || "User"}</strong>  
        <small>{currentUser?.email || "Authenticated account"}</small>
    </div>


</div>
</aside>

            <main className="main-content" id="dashboard">
                <header className="topbar">
                    <div>
                        <p className="breadcrumb">Workspace / Dashboard</p>
                        <h2>Dashboard</h2>
                    </div>

                  <div className="topbar-right">
    <span className="status">
        <span className="status-dot"></span>
        Connected
    </span>

    <div className="profile-avatar">
        {currentUser?.name?.charAt(0).toUpperCase() || "U"}
    </div>

    <button
        className="logout-button"
        onClick={handleLogout}
    >
        Logout
    </button>
</div>
                </header>

                <section className="welcome">
                    <div>
                        <p className="eyebrow">
                            CLOUD INTELLIGENCE PLATFORM
                        </p>
                        <h1>Welcome to ChooseCloud</h1>
                        <p>
                            Compare cloud providers and discover the right
                            infrastructure for your workload.
                        </p>
                    </div>
                    <div className="welcome-icon">☁</div>
                </section>

                <section className="stats-grid">
                    <div className="stat-card">
                        <span>Cloud Providers</span>
                        <h2>
                            {loading
                                ? "..."
                                : providers.length.toString().padStart(2, "0")}
                        </h2>
                        <small>AWS, Azure and Google Cloud</small>
                    </div>

                    <div className="stat-card">
                        <span>Pricing Records</span>
                        <h2>
                            {loading
                                ? "..."
                                : prices.length.toString().padStart(2, "0")}
                        </h2>
                        <small>Available service pricing records</small>
                    </div>
<div className="stat-card">
    <span>Service Categories</span>
    <h2>
        {new Set(prices.map((price) => price.category)).size
            .toString()
            .padStart(2, "0")}
    </h2>
    <small>Compute, Storage and Database</small>
</div>
                </section>

                <section className="section" id="providers">
                    <div className="section-heading">
                        <div>
                            <h2>Cloud Providers</h2>
                            <p>
                                Explore the providers supported by our platform.
                            </p>
                        </div>
                    </div>

                    <div className="provider-grid">
                        {loading && <p>Loading cloud providers...</p>}

                        {error && <p>{error}</p>}

                        {!loading && !error && providers.map((provider) => (
                            <div className="provider-card" key={provider.id}>
                                <div
                                    className="provider-icon"
                                    style={{
                                        color:
                                            providerColors[provider.code] ||
                                            "#38bdf8"
                                    }}
                                >
                                    ☁
                                </div>

                                <h3>{provider.name}</h3>
                                <p>{provider.description}</p>

                                <span className="provider-tag">
                                    {provider.code}
                                </span>
                            </div>
                        ))}
                    </div>
                </section>

                <section className="pricing-section" id="pricing">
                    <div className="section-heading">
                        <div>
                            <p className="eyebrow">MULTI-CLOUD COST ENGINE</p>
                            <h2>Compute Cost Comparison</h2>
                            <p>
                                Compare estimated infrastructure costs
                                across AWS, Azure and Google Cloud.
                            </p>
                        </div>
                    </div>

                    <div className="usage-box">
                        <label htmlFor="usage-hours">
                            Required usage hours
                        </label>

                        <input
                            id="usage-hours"
                            type="number"
                            min="1"
                            step="1"
                            value={hours}
                            onChange={(e) => setHours(e.target.value)}
                            placeholder="Enter usage hours"
                        />

                        <button
                            onClick={calculateCosts}
                            disabled={loading || calculating || computePrices.length === 0}
                        >
                            {calculating
                                ? "Calculating..."
                                : "Calculate Cloud Costs"}
                        </button>
                    </div>

                    {pricingError && (
                        <p className="pricing-error">{pricingError}</p>
                    )}

                    {estimates.length > 0 && (
                        <>
                            <div className="comparison-grid">
                                {estimates.map((item) => (
                                    <div
                                        className={`cost-card ${
                                            item.estimated_cost_inr === cheapestCost
                                                ? "cheapest-card"
                                                : ""
                                        }`}
                                        key={item.price_id}
                                    >
                                        {item.estimated_cost_inr === cheapestCost && (
                                            <span className="cheapest-label">
                                                LOWEST COST
                                            </span>
                                        )}

                                        <h3>{item.provider}</h3>

                                        <p>{item.service}</p>

                                        <h2>
                                            {formatINR(item.estimated_cost_inr)}
                                        </h2>

                                        <span>Estimated total cost</span>

                                        <div className="cost-details">
                                            <p>
                                                <strong>Region:</strong>{" "}
                                                {item.region}
                                            </p>
                                            <p>
                                                <strong>Usage:</strong>{" "}
                                                {item.usage_quantity} hours
                                            </p>
                                            <p>
                                                <strong>Hourly price:</strong>{" "}
                                                {item.original_currency}{" "}
                                                {(
                                                    item.original_cost /
                                                    item.usage_quantity
                                                ).toFixed(6)}
                                            </p>
                                            <p>
                                                <strong>Configuration:</strong>{" "}
                                                {item.configuration}
                                            </p>
                                        </div>
                                    </div>
                                ))}
                            </div>

                            <div className="winner-panel">
                                <p className="eyebrow">
                                    COST COMPARISON RESULT
                                </p>
                                <h2>
                                    {estimates.find(
                                        item =>
                                            item.estimated_cost_inr === cheapestCost
                                    )?.provider}{" "}
                                    is currently the lowest-cost option.
                                </h2>
                                <p>
                                    Estimated cost: {formatINR(cheapestCost)}
                                    {" "}for {hours} hours.
                                </p>
                            </div>
                        </>
                    )}
                </section>

<section className="pricing-section" id="storage">
    <div className="section-heading">
        <div>
            <p className="eyebrow">MULTI-CLOUD STORAGE ENGINE</p>
            <h2>Storage Cost Comparison</h2>
            <p>
                Compare monthly storage costs across AWS,
                Azure and Google Cloud.
            </p>
        </div>
    </div>

    <div className="usage-box">
        <label htmlFor="storage-gb">
            Required storage capacity (GB)
        </label>

        <input
            id="storage-gb"
            type="number"
            min="1"
            step="1"
            value={storageGb}
            onChange={(e) => setStorageGb(e.target.value)}
            placeholder="Enter storage in GB"
        />

        <button
            onClick={calculateStorageCosts}
            disabled={storageCalculating}
        >
            {storageCalculating
                ? "Calculating..."
                : "Calculate Storage Costs"}
        </button>
    </div>

    {storageError && (
        <p className="pricing-error">{storageError}</p>
    )}

    {storageEstimates.length > 0 && (
        <>
            <div className="comparison-grid">
                {storageEstimates.map((item) => {
                    const lowest = Math.min(
                        ...storageEstimates.map(
                            result => result.estimated_cost_inr
                        )
                    );

                    return (
                        <div
                            className={`cost-card ${
                                item.estimated_cost_inr === lowest
                                    ? "cheapest-card"
                                    : ""
                            }`}
                            key={item.service}
                        >
                            {item.estimated_cost_inr === lowest && (
                                <span className="cheapest-label">
                                    LOWEST COST
                                </span>
                            )}

                            <h3>{item.provider}</h3>
                            <p>{item.service}</p>

                            <h2>
                                {formatINR(item.estimated_cost_inr)}
                            </h2>

                            <span>Estimated monthly cost</span>

                            <div className="cost-details">
                                <p>
                                    <strong>Region:</strong>{" "}
                                    {item.region}
                                </p>
                                <p>
                                    <strong>Storage:</strong>{" "}
                                    {item.storage_gb} GB
                                </p>
                                <p>
                                    <strong>Price per GB:</strong>{" "}
                                    ${Number(
                                        item.price_per_gb_month
                                    ).toFixed(4)}
                                </p>
                                <p>
                                    <strong>Configuration:</strong>{" "}
                                    {item.configuration}
                                </p>
                            </div>
                        </div>
                    );
                })}
            </div>

            <div className="winner-panel">
                <p className="eyebrow">
                    STORAGE COMPARISON RESULT
                </p>

                <h2>
                    {
                        storageEstimates.reduce(
                            (lowest, current) =>
                                current.estimated_cost_inr <
                                lowest.estimated_cost_inr
                                    ? current
                                    : lowest
                        ).provider
                    }{" "}
                    is currently the lowest-cost option.
                </h2>

                <p>
                    Estimated monthly cost:{" "}
                    {formatINR(
                        Math.min(
                            ...storageEstimates.map(
                                item => item.estimated_cost_inr
                            )
                        )
                    )}
                </p>
            </div>
        </>
    )}
</section>

<section className="pricing-section" id="database">
    <div className="section-heading">
        <div>
            <p className="eyebrow">MULTI-CLOUD DATABASE ENGINE</p>
            <h2>Database Cost Comparison</h2>
            <p>
                Compare PostgreSQL database compute and storage
                costs across AWS, Azure and Google Cloud.
            </p>
        </div>
    </div>

    <div className="usage-box">
        <label htmlFor="database-hours">
            Database usage hours per month
        </label>

        <input
            id="database-hours"
            type="number"
            min="1"
            max="744"
            value={databaseHours}
            onChange={(e) => setDatabaseHours(e.target.value)}
            placeholder="Enter usage hours"
        />

        <label htmlFor="database-storage">
            Required database storage (GB)
        </label>

        <input
            id="database-storage"
            type="number"
            min="1"
            value={databaseStorageGb}
            onChange={(e) => setDatabaseStorageGb(e.target.value)}
            placeholder="Enter storage capacity"
        />

        <button
            onClick={calculateDatabaseCosts}
            disabled={databaseCalculating}
        >
            {databaseCalculating
                ? "Calculating..."
                : "Compare Database Costs"}
        </button>
    </div>

    {databaseError && (
        <p className="pricing-error">{databaseError}</p>
    )}

    {databaseEstimates.length > 0 && (
        <>
            <div className="comparison-grid">
                {databaseEstimates.map((item) => {
                    const lowest = Math.min(
                        ...databaseEstimates.map(
                            result => result.estimated_cost_inr
                        )
                    );

                    return (
                        <div
                            className={`cost-card ${
                                item.estimated_cost_inr === lowest
                                    ? "cheapest-card"
                                    : ""
                            }`}
                            key={item.provider}
                        >
                            {item.estimated_cost_inr === lowest && (
                                <span className="cheapest-label">
                                    LOWEST COST
                                </span>
                            )}

                            <h3>{item.provider}</h3>
                            <p>{item.service}</p>

                            <h2>
                                {formatINR(item.estimated_cost_inr)}
                            </h2>

                            <span>Estimated monthly cost</span>

                            <div className="cost-details">
                                <p>
                                    <strong>Region:</strong>{" "}
                                    {item.region}
                                </p>

                                <p>
                                    <strong>Usage:</strong>{" "}
                                    {item.usage_hours} hours
                                </p>

                                <p>
                                    <strong>Storage:</strong>{" "}
                                    {item.storage_gb} GB
                                </p>

                                <p>
                                    <strong>Compute cost:</strong>{" "}
                                    {formatINR(item.compute_cost_inr)}
                                </p>

                                <p>
                                    <strong>Storage cost:</strong>{" "}
                                    {formatINR(item.storage_cost_inr)}
                                </p>

                                <p>
                                    <strong>Total in USD:</strong>{" "}
                                    ${item.total_cost_usd}
                                </p>

                                <p>
                                    <strong>Compute configuration:</strong>{" "}
                                    {item.compute_configuration}
                                </p>

                                <p>
                                    <strong>Storage configuration:</strong>{" "}
                                    {item.storage_configuration}
                                </p>
                            </div>
                        </div>
                    );
                })}
            </div>

            <div className="winner-panel">
                <p className="eyebrow">
                    DATABASE COMPARISON RESULT
                </p>

                <h2>
                    {databaseEstimates[0].provider} is currently
                    the lowest-cost option.
                </h2>

                <p>
                    Estimated monthly cost:{" "}
                    {formatINR(
                        databaseEstimates[0].estimated_cost_inr
                    )}
                </p>
            </div>
        </>
    )}
</section>

                <section className="recommendation-panel" id="recommendations">
                    <div className="recommendation-inputs">
    <p className="eyebrow">SMART CLOUD RECOMMENDATION</p>
    <h2>Find the Best Cloud Provider</h2>
    <p>Enter your workload requirements to compare AWS, Azure and Google Cloud.</p>

    <div className="usage-box">
        <label>Compute usage (hours/month)</label>
        <input
            type="number"
            min="1"
            max="744"
            value={recommendationInputs.compute_hours}
            onChange={(e) =>
                setRecommendationInputs({
                    ...recommendationInputs,
                    compute_hours: e.target.value
                })
            }
        />

        <label>Storage requirement (GB)</label>
        <input
            type="number"
            min="1"
            value={recommendationInputs.storage_gb}
            onChange={(e) =>
                setRecommendationInputs({
                    ...recommendationInputs,
                    storage_gb: e.target.value
                })
            }
        />

        <label>Database usage (hours/month)</label>
        <input
            type="number"
            min="1"
            max="744"
            value={recommendationInputs.database_hours}
            onChange={(e) =>
                setRecommendationInputs({
                    ...recommendationInputs,
                    database_hours: e.target.value
                })
            }
        />

        <label>Database storage (GB)</label>
        <input
            type="number"
            min="1"
            value={recommendationInputs.database_storage_gb}
            onChange={(e) =>
                setRecommendationInputs({
                    ...recommendationInputs,
                    database_storage_gb: e.target.value
                })
            }
        />

        <button
            onClick={generateRecommendation}
            disabled={recommendationLoading}
        >
            {recommendationLoading
                ? "Analyzing..."
                : "Recommend Cloud Provider"}
        </button>
    </div>

    {recommendationError && (
        <p className="pricing-error">{recommendationError}</p>
    )}
</div>
                  {recommendation && (
    <div className="winner-panel">
        <p className="eyebrow">YOUR CLOUD RECOMMENDATION</p>

        <h2>
            {recommendation.recommended_provider}
        </h2>

        <h3>
            {formatINR(
                recommendation.estimated_total_cost_inr
            )}
        </h3>

        <p>Estimated combined monthly cost</p>

        <p>
            Recommended using:
            {" "}
            {recommendation.recommendation_type}
        </p>

        <h3>Provider Cost Breakdown</h3>

        <div className="comparison-grid">
            {recommendation.results.map((item) => (
                <div className="cost-card" key={item.provider}>
                    <h3>{item.provider}</h3>

                    <h2>
                        {formatINR(
                            item.total_estimated_cost_inr
                        )}
                    </h2>

                    <p>Estimated monthly cost</p>

                    <div className="cost-details">
                        <p>
                            Compute: {formatINR(item.compute_cost_inr)}
                        </p>

                        <p>
                            Storage: {formatINR(item.storage_cost_inr)}
                        </p>

                        <p>
                            Database compute:{" "}
                            {formatINR(item.database_compute_cost_inr)}
                        </p>

                        <p>
                            Database storage:{" "}
                            {formatINR(item.database_storage_cost_inr)}
                        </p>
                    </div>
                </div>
            ))}
        </div>
    </div>
)}
                </section>
<section className="forecast-panel" id="forecast">
    
                    <div className="section-heading">
                        <div>
                            <p className="eyebrow">MACHINE LEARNING</p>
                            <h2>Workload Forecast</h2>
                            <p>
                                Predict aggregated data-centre CPU and memory
                                usage using historical workload observations.
                            </p>
                        </div>
                    </div>

                    <div className="forecast-controls">
                        <div>
                            <label htmlFor="forecast-horizon">
                                Forecast Horizon
                            </label>

                            <select
                                id="forecast-horizon"
                                value={forecastHorizon}
                                onChange={(e) => {
                                    setForecastHorizon(e.target.value);
                                    setForecastResult(null);
                                }}
                            >
                                <option value="5">5 Minutes</option>
                                <option value="10">10 Minutes</option>
                                <option value="15">15 Minutes</option>
                            </select>
                        </div>

                        <button
                            onClick={generateWorkloadForecast}
                            disabled={forecastLoading}
                        >
                            {forecastLoading
                                ? "Generating Forecast..."
                                : "Generate Forecast"}
                        </button>
                    </div>

                    {forecastError && (
                        <p className="pricing-error">
                            {forecastError}
                        </p>
                    )}

                    {forecastResult && (
                        <div className="forecast-results">
                            <div className="forecast-card">
                                <p>Predicted CPU Usage</p>
                                <h3>
                                    {forecastResult.predicted_avg_cpu_percentage.toFixed(2)}%
                                </h3>
                                <span>
                                    {forecastResult.forecast_horizon_minutes}-minute forecast
                                </span>
                            </div>

                            <div className="forecast-card">
                                <p>Predicted Memory Usage</p>
                                <h3>
                                    {forecastResult.predicted_avg_memory_percentage.toFixed(2)}%
                                </h3>
                                <span>
                                    {forecastResult.forecast_horizon_minutes}-minute forecast
                                </span>
                            </div>

                            <p className="forecast-source">
                                Model: {forecastResult.model} |
                                Source: bundled aggregated data-centre workload dataset.
                                Not live cloud telemetry.
                            </p>
                        </div>
                    )}
                </section>

                <section className="cloudshift-panel" id="cloudshift">
                    <div className="section-heading">
                        <div>
                            <p className="eyebrow">INTELLIGENT CLOUD MIGRATION</p>
                            <h2>CloudShift – Migration Advisor</h2>
                            <p>
                                Compare cloud infrastructure costs and discover
                                potential savings when moving between providers.
                            </p>
                        </div>
                    </div>

                    <div className="cloudshift-controls">
                        <div>
                            <label>Current Cloud Provider</label>
                            <select
                                value={cloudShiftSource}
                                onChange={(e) => {
                                    setCloudShiftSource(e.target.value);
                                    setCloudShiftResult(null);
                                    setCloudShiftError("");
                                }}
                            >
                                <option value="Amazon Web Services">
                                    Amazon Web Services
                                </option>
                                <option value="Microsoft Azure">
                                    Microsoft Azure
                                </option>
                                <option value="Google Cloud">
                                    Google Cloud
                                </option>
                            </select>
                        </div>

                        <div>
                            <label>Target Cloud Provider</label>
                            <select
                                value={cloudShiftTarget}
                                onChange={(e) => {
                                    setCloudShiftTarget(e.target.value);
                                    setCloudShiftResult(null);
                                    setCloudShiftError("");
                                }}
                            >
                                <option value="Amazon Web Services">
                                    Amazon Web Services
                                </option>
                                <option value="Microsoft Azure">
                                    Microsoft Azure
                                </option>
                                <option value="Google Cloud">
                                    Google Cloud
                                </option>
                            </select>
                        </div>
                    </div>

                    <div className="cloudshift-input-grid">
                        <div>
                            <label>Compute Hours / Month</label>
                            <input
                                type="number"
                                min="1"
                                max="744"
                                value={cloudShiftInputs.compute_hours}
                                onChange={(e) =>
                                    setCloudShiftInputs({
                                        ...cloudShiftInputs,
                                        compute_hours: e.target.value
                                    })
                                }
                            />
                        </div>

                        <div>
                            <label>Storage Requirement (GB)</label>
                            <input
                                type="number"
                                min="1"
                                value={cloudShiftInputs.storage_gb}
                                onChange={(e) =>
                                    setCloudShiftInputs({
                                        ...cloudShiftInputs,
                                        storage_gb: e.target.value
                                    })
                                }
                            />
                        </div>

                        <div>
                            <label>Database Hours / Month</label>
                            <input
                                type="number"
                                min="1"
                                max="744"
                                value={cloudShiftInputs.database_hours}
                                onChange={(e) =>
                                    setCloudShiftInputs({
                                        ...cloudShiftInputs,
                                        database_hours: e.target.value
                                    })
                                }
                            />
                        </div>

                        <div>
                            <label>Database Storage (GB)</label>
                            <input
                                type="number"
                                min="1"
                                value={cloudShiftInputs.database_storage_gb}
                                onChange={(e) =>
                                    setCloudShiftInputs({
                                        ...cloudShiftInputs,
                                        database_storage_gb: e.target.value
                                    })
                                }
                            />
                        </div>
                    </div>

                    <button
                        onClick={generateCloudShiftAnalysis}
                        disabled={
                            cloudShiftLoading ||
                            cloudShiftSource === cloudShiftTarget
                        }
                    >
                        {cloudShiftLoading
                            ? "Analyzing Migration..."
                            : "Analyze Cloud Migration"}
                    </button>

                    {cloudShiftSource === cloudShiftTarget && (
                        <p className="pricing-error">
                            Select two different cloud providers.
                        </p>
                    )}

                    {cloudShiftError && (
                        <p className="pricing-error">
                            {cloudShiftError}
                        </p>
                    )}

                    {cloudShiftResult && (
                        <div className="cloudshift-results">
                            <div className="cloudshift-summary">
                                <div>
                                    <p>Current Monthly Cost</p>
                                    <h3>
                                        ₹{cloudShiftResult.source_monthly_cost_inr.toLocaleString("en-IN")}
                                    </h3>
                                </div>

                                <div>
                                    <p>Target Monthly Cost</p>
                                    <h3>
                                        ₹{cloudShiftResult.target_monthly_cost_inr.toLocaleString("en-IN")}
                                    </h3>
                                </div>

                                <div>
                                    <p>Potential Monthly Savings</p>
                                    <h3>
                                        ₹{cloudShiftResult.estimated_monthly_savings_inr.toLocaleString("en-IN")}
                                    </h3>
                                    <span>
                                        {cloudShiftResult.estimated_savings_percentage}% estimated
                                    </span>
                                </div>
                            </div>

                            <h3>{cloudShiftResult.recommendation}</h3>

                            <h3>Service Migration Mapping</h3>

                            <div className="cloudshift-mapping-list">
                                {cloudShiftResult.service_mappings.map(
                                    (item, index) => (
                                        <div
                                            className="cloudshift-mapping-card"
                                            key={index}
                                        >
                                            <p>{item.category}</p>
                                            <h4>{item.source_service}</h4>
                                            <p>↓</p>
                                            <h4>{item.target_service}</h4>
                                            <span>{item.mapping_reason}</span>

                                            <div>
                                                <p>
                                                    Current: ₹{item.source_monthly_cost_inr.toLocaleString("en-IN")}
                                                </p>
                                                <p>
                                                    Target: ₹{item.target_monthly_cost_inr.toLocaleString("en-IN")}
                                                </p>
                                            </div>
                                        </div>
                                    )
                                )}
                            </div>

                            <div className="cloudshift-readiness">
                                <h3>Migration Readiness Checklist</h3>
                                <p>
                                    Review these requirements before starting
                                    an actual cloud migration.
                                </p>

                                <div className="cloudshift-readiness-grid">
                                    {cloudShiftResult.migration_readiness_checks.map(
                                        (check, index) => (
                                            <div
                                                className="cloudshift-readiness-card"
                                                key={index}
                                            >
                                                <span>
                                                    {String(index + 1).padStart(2, "0")}
                                                </span>
                                                <h4>{check.title}</h4>
                                                <p>{check.description}</p>
                                            </div>
                                        )
                                    )}
                                </div>
                            </div>

                            <p className="forecast-source">
                                {cloudShiftResult.notice}
                            </p>
                        </div>
                    )}
                </section>
<section id="history" className="section">
    <div className="section-header">
        <div>
            <h2>Activity History</h2>
            <p>Previously generated comparisons and migration analyses</p>
        </div>

        <button
            className="secondary-button"
            onClick={() => {
    const confirmed = window.confirm(
        "Are you sure you want to clear all activity history?"
    );

    if (confirmed) {
        setHistory([]);
        localStorage.removeItem("choosecloud_history");
    }
}}
            disabled={history.length === 0}
        >
            Clear History
        </button>
    </div>

    <div className="history-list">
        {history.length === 0 ? (
            <div className="empty-state">
                <h3>No activity yet</h3>
                <p>
                    Your successful cost comparisons,
                    recommendations and CloudShift analyses
                    will appear here.
                </p>
            </div>
        ) : (
          history.map((item) => (
    <div className="history-card" key={item.id}>
        <div className="history-card-content">
            <h3>{item.type}</h3>

            <p>{item.summary}</p>

            <small>{item.createdAt}</small>

            {item.type === "CloudShift Migration Analysis" &&
                item.details && (
                    <div className="history-migration-details">

                        <div className="history-cost-grid">
                            <div>
                                <span>Source Monthly Cost</span>
                                <strong>
                                    {formatINR(
                                        item.details.source_monthly_cost_inr
                                    )}
                                </strong>
                            </div>

                            <div>
                                <span>Target Monthly Cost</span>
                                <strong>
                                    {formatINR(
                                        item.details.target_monthly_cost_inr
                                    )}
                                </strong>
                            </div>

                            <div>
                                <span>Estimated Monthly Savings</span>
                                <strong className="history-savings">
                                    {formatINR(
                                        item.details.estimated_monthly_savings_inr
                                    )}
                                </strong>
                            </div>
                        </div>

                        <p>
                            Savings percentage:{" "}
                            <strong>
                                {item.details.estimated_savings_percentage}%
                            </strong>
                        </p>

                        <p className="history-provider-route">
                            {item.details.source_provider} →{" "}
                            {item.details.target_provider}
                        </p>

                    </div>
                )}
        </div>
    </div>
))
        )}
    </div>
</section>
                <footer>
                    ChooseCloud © 2026 | Intelligent Multi-Cloud Platform
                </footer>
            </main>
        </div>
    );
}

export default App;
