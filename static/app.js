/* =========================================================================
   OSINT AGGREGATOR — frontend logic
   Không đổi hợp đồng API (GET /api/categories, POST /api/search) — chỉ đổi
   cách render. Muốn thêm 1 loại placeholder mới cho category mới? Sửa
   PLACEHOLDER_BY_CATEGORY bên dưới là đủ, không cần sửa gì khác trong file.
   ========================================================================= */

const PLACEHOLDER_BY_CATEGORY = {
    domain: "example.com",
    ip: "8.8.8.8",
    username: "octocat",
    email: "name@example.com",
};

// Nhãn hiển thị trên "con dấu" theo từng status connector trả về.
// Thêm status mới ở đây nếu sau này bạn mở rộng schema.
const STAMP_BY_STATUS = {
    ok: { label: "Verified", className: "stamp--ok" },
    error: { label: "Unavailable", className: "stamp--error" },
    no_data: { label: "No record", className: "stamp--pending" },
};

const tabsContainer = document.getElementById("category-tabs");
const targetInput = document.getElementById("target-input");
const form = document.getElementById("search-form");
const submitBtn = document.getElementById("submit-btn");
const statusMessage = document.getElementById("status-message");
const resultsContainer = document.getElementById("results");
const emptyState = document.getElementById("empty-state");
const refCode = document.getElementById("ref-code");

let selectedCategory = null;

// -------------------------------------------------------------------------
// Khởi tạo
// -------------------------------------------------------------------------

setRefDate();
loadCategories();
toggleEmptyState(true);

function setRefDate() {
    const now = new Date();
    const y = now.getFullYear();
    const m = String(now.getMonth() + 1).padStart(2, "0");
    const d = String(now.getDate()).padStart(2, "0");
    refCode.textContent = `PUBLIC-SOURCE-INTEL · ${y}-${m}-${d}`;
}

// -------------------------------------------------------------------------
// 1. Tải danh mục -> render tab. Dropdown cũ đã được thay bằng tab để giao
//    diện gần với "cặp hồ sơ" hơn, nhưng logic vẫn: 1 tab = 1 category.
// -------------------------------------------------------------------------

async function loadCategories() {
    try {
        const res = await fetch("/api/categories");
        const categories = await res.json();

        tabsContainer.innerHTML = "";

        if (categories.length === 0) {
            tabsContainer.innerHTML =
                '<span class="tabs-loading">Chưa có connector nào được đăng ký.</span>';
            return;
        }

        categories.forEach((cat, index) => {
            const tab = document.createElement("button");
            tab.type = "button";
            tab.className = "tab-btn";
            tab.role = "tab";
            tab.dataset.category = cat.category;
            tab.setAttribute("aria-selected", index === 0 ? "true" : "false");
            tab.textContent = cat.category;
            tab.title = cat.connectors.map((c) => c.display_name).join(", ");
            tab.addEventListener("click", () => selectCategory(cat.category));
            tabsContainer.appendChild(tab);
        });

        selectCategory(categories[0].category);
    } catch (err) {
        tabsContainer.innerHTML =
            '<span class="tabs-loading">Không tải được danh mục.</span>';
        console.error(err);
    }
}

function selectCategory(category) {
    selectedCategory = category;

    tabsContainer.querySelectorAll(".tab-btn").forEach((btn) => {
        btn.setAttribute("aria-selected", btn.dataset.category === category ? "true" : "false");
    });

    targetInput.placeholder = PLACEHOLDER_BY_CATEGORY[category] || "";
}

// -------------------------------------------------------------------------
// 2. Submit form
// -------------------------------------------------------------------------

form.addEventListener("submit", async (event) => {
    event.preventDefault();

    const target = targetInput.value.trim();
    if (!selectedCategory || !target) return;

    setLoading(true);
    statusMessage.textContent = "";
    statusMessage.className = "status-message";
    resultsContainer.innerHTML = "";
    toggleEmptyState(false);

    try {
        const res = await fetch("/api/search", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ category: selectedCategory, target }),
        });

        const data = await res.json();

        if (!res.ok) {
            statusMessage.textContent = data.error || "Có lỗi xảy ra.";
            statusMessage.className = "status-message error";
            toggleEmptyState(true);
            return;
        }

        if (data.message) {
            statusMessage.textContent = data.message;
        }

        if (!data.results || data.results.length === 0) {
            toggleEmptyState(true);
            return;
        }

        renderResults(data.results);
    } catch (err) {
        statusMessage.textContent = "Không thể kết nối tới server.";
        statusMessage.className = "status-message error";
        toggleEmptyState(true);
        console.error(err);
    } finally {
        setLoading(false);
    }
});

function setLoading(isLoading) {
    submitBtn.disabled = isLoading;
    submitBtn.textContent = isLoading ? "Searching…" : "Run search";
}

function toggleEmptyState(visible) {
    emptyState.classList.toggle("visible", visible);
}

// -------------------------------------------------------------------------
// 3. Render kết quả -- mỗi connector = 1 .file-card. Chỉ hiển thị raw_data,
//    không thêm bất kỳ diễn giải/kết luận nào ở đây.
// -------------------------------------------------------------------------

function renderResults(results) {
    for (const result of results) {
        resultsContainer.appendChild(buildFileCard(result));
    }
}

function buildFileCard(result) {
    const card = document.createElement("article");
    card.className = "file-card";

    const tab = document.createElement("div");
    tab.className = "file-card-tab";

    const titleWrap = document.createElement("div");
    const title = document.createElement("h3");
    title.className = "file-card-title";
    title.textContent = result.display_name;

    const meta = document.createElement("div");
    meta.className = "file-card-meta";
    meta.textContent = `Source: ${result.source}`;
    if (result.from_cache) {
        const cacheNote = document.createElement("span");
        cacheNote.className = "cache-note";
        cacheNote.textContent = "(cached)";
        meta.appendChild(cacheNote);
    }

    titleWrap.appendChild(title);
    titleWrap.appendChild(meta);

    const stampInfo = STAMP_BY_STATUS[result.status] || {
        label: result.status,
        className: "stamp--pending",
    };
    const stamp = document.createElement("span");
    stamp.className = `stamp ${stampInfo.className}`;
    stamp.textContent = stampInfo.label;

    tab.appendChild(titleWrap);
    tab.appendChild(stamp);
    card.appendChild(tab);

    const body = document.createElement("div");
    body.className = "file-card-body";

    if (result.status === "error") {
        const note = document.createElement("p");
        note.className = "file-card-note error-text";
        note.textContent = result.error_message || "Lỗi không xác định.";
        body.appendChild(note);
    } else if (result.status === "no_data" || !result.raw_data) {
        const note = document.createElement("p");
        note.className = "file-card-note";
        note.textContent = "Không có dữ liệu công khai cho subject này.";
        body.appendChild(note);
    } else {
        body.appendChild(buildDataList(result.raw_data));
    }

    card.appendChild(body);
    return card;
}

function buildDataList(rawData) {
    const dl = document.createElement("dl");
    dl.style.margin = "0";

    for (const [key, value] of Object.entries(rawData)) {
        const row = document.createElement("div");
        row.className = "data-row";

        const dt = document.createElement("dt");
        dt.textContent = key;

        const dd = document.createElement("dd");
        dd.textContent = formatValue(value);

        row.appendChild(dt);
        row.appendChild(dd);
        dl.appendChild(row);
    }

    return dl;
}

function formatValue(value) {
    if (value === null || value === undefined) return "—";
    if (Array.isArray(value)) return value.length ? value.join(", ") : "—";
    return String(value);
}
