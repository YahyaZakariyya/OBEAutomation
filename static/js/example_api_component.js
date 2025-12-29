/**
 * Example Vue.js Component for consuming DRF APIs
 *
 * This component demonstrates how to:
 * - Fetch data from DRF APIs
 * - Handle pagination
 * - Implement search and filtering
 * - Handle errors and loading states
 * - Update and create data via API
 *
 * API Endpoints Available:
 * - GET /api/programs/ - List all programs (with pagination)
 * - GET /api/programs/{id}/ - Get program details
 * - POST /api/programs/ - Create program
 * - PUT /api/programs/{id}/ - Update program
 * - DELETE /api/programs/{id}/ - Delete program
 *
 * Similar endpoints available for:
 * - /api/users/
 * - /api/courses/
 * - /api/sections/
 * - /api/assessments/
 * - /api/questions/
 * - /api/clos/
 * - /api/plos/
 * etc.
 */

const { createApp } = Vue;

const ExampleAPIComponent = {
    template: `
        <div class="container">
            <!-- Loading State -->
            <div v-if="loading" class="alert alert-info">
                <span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span>
                Loading...
            </div>

            <!-- Error State -->
            <div v-if="error" class="alert alert-danger alert-dismissible fade show" role="alert">
                <strong>Error!</strong> {{ error }}
                <button type="button" class="btn-close" @click="error = null"></button>
            </div>

            <!-- Search and Filter -->
            <div class="row mb-3">
                <div class="col-md-6">
                    <input
                        type="text"
                        class="form-control"
                        v-model="searchQuery"
                        @input="debouncedSearch"
                        placeholder="Search..."
                    >
                </div>
                <div class="col-md-3">
                    <select v-model="filterType" @change="fetchData" class="form-control">
                        <option value="">All Types</option>
                        <option value="UG">Undergraduate</option>
                        <option value="GR">Graduate</option>
                        <option value="PG">Postgraduate</option>
                    </select>
                </div>
                <div class="col-md-3">
                    <button @click="showCreateModal" class="btn btn-primary">
                        <i class="fas fa-plus"></i> Add New
                    </button>
                </div>
            </div>

            <!-- Data Table -->
            <div v-if="!loading && items.length > 0" class="table-responsive">
                <table class="table table-striped table-hover">
                    <thead>
                        <tr>
                            <th @click="sortBy('id')" style="cursor: pointer;">
                                ID <i :class="getSortIcon('id')"></i>
                            </th>
                            <th @click="sortBy('program_abbreviation')" style="cursor: pointer;">
                                Abbreviation <i :class="getSortIcon('program_abbreviation')"></i>
                            </th>
                            <th>Title</th>
                            <th>Type</th>
                            <th>Actions</th>
                        </tr>
                    </thead>
                    <tbody>
                        <tr v-for="item in items" :key="item.id">
                            <td>{{ item.id }}</td>
                            <td>{{ item.program_abbreviation }}</td>
                            <td>{{ item.program_title }}</td>
                            <td>{{ item.program_type }}</td>
                            <td>
                                <button @click="viewDetails(item.id)" class="btn btn-sm btn-info me-1">
                                    <i class="fas fa-eye"></i>
                                </button>
                                <button @click="editItem(item)" class="btn btn-sm btn-warning me-1">
                                    <i class="fas fa-edit"></i>
                                </button>
                                <button @click="deleteItem(item.id)" class="btn btn-sm btn-danger">
                                    <i class="fas fa-trash"></i>
                                </button>
                            </td>
                        </tr>
                    </tbody>
                </table>
            </div>

            <!-- Empty State -->
            <div v-if="!loading && items.length === 0" class="alert alert-warning">
                No items found.
            </div>

            <!-- Pagination -->
            <nav v-if="pagination.count > pagination.page_size" aria-label="Page navigation">
                <ul class="pagination">
                    <li class="page-item" :class="{ disabled: !pagination.previous }">
                        <a class="page-link" @click="goToPage(currentPage - 1)" href="#">Previous</a>
                    </li>
                    <li
                        v-for="page in totalPages"
                        :key="page"
                        class="page-item"
                        :class="{ active: page === currentPage }"
                    >
                        <a class="page-link" @click="goToPage(page)" href="#">{{ page }}</a>
                    </li>
                    <li class="page-item" :class="{ disabled: !pagination.next }">
                        <a class="page-link" @click="goToPage(currentPage + 1)" href="#">Next</a>
                    </li>
                </ul>
            </nav>
        </div>
    `,

    data() {
        return {
            items: [],
            loading: false,
            error: null,
            searchQuery: '',
            filterType: '',
            currentPage: 1,
            ordering: null,
            pagination: {
                count: 0,
                next: null,
                previous: null,
                page_size: 50
            },
            debounceTimeout: null
        };
    },

    computed: {
        totalPages() {
            return Math.ceil(this.pagination.count / this.pagination.page_size);
        }
    },

    mounted() {
        this.fetchData();
    },

    methods: {
        /**
         * Fetch data from API with pagination, search, and filtering
         */
        async fetchData() {
            this.loading = true;
            this.error = null;

            try {
                // Build query parameters
                const params = new URLSearchParams();
                params.append('page', this.currentPage);

                if (this.searchQuery) {
                    params.append('search', this.searchQuery);
                }

                if (this.filterType) {
                    params.append('type', this.filterType);
                }

                if (this.ordering) {
                    params.append('ordering', this.ordering);
                }

                // Fetch data
                const response = await fetch(`/api/programs/?${params.toString()}`, {
                    headers: {
                        'Content-Type': 'application/json',
                        'X-CSRFToken': this.getCookie('csrftoken')
                    }
                });

                if (!response.ok) {
                    throw new Error(`HTTP error! status: ${response.status}`);
                }

                const data = await response.json();

                // Update state
                this.items = data.results || [];
                this.pagination = {
                    count: data.count,
                    next: data.next,
                    previous: data.previous,
                    page_size: this.pagination.page_size
                };

            } catch (err) {
                this.error = err.message;
                console.error('Error fetching data:', err);
            } finally {
                this.loading = false;
            }
        },

        /**
         * Fetch single item details
         */
        async viewDetails(id) {
            this.loading = true;
            this.error = null;

            try {
                const response = await fetch(`/api/programs/${id}/`, {
                    headers: {
                        'Content-Type': 'application/json',
                        'X-CSRFToken': this.getCookie('csrftoken')
                    }
                });

                if (!response.ok) {
                    throw new Error(`HTTP error! status: ${response.status}`);
                }

                const data = await response.json();
                console.log('Item details:', data);
                // Handle showing details (e.g., open modal, navigate, etc.)

            } catch (err) {
                this.error = err.message;
                console.error('Error fetching details:', err);
            } finally {
                this.loading = false;
            }
        },

        /**
         * Create new item
         */
        async createItem(itemData) {
            this.loading = true;
            this.error = null;

            try {
                const response = await fetch('/api/programs/', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'X-CSRFToken': this.getCookie('csrftoken')
                    },
                    body: JSON.stringify(itemData)
                });

                if (!response.ok) {
                    const errorData = await response.json();
                    throw new Error(JSON.stringify(errorData));
                }

                const data = await response.json();
                console.log('Created item:', data);

                // Refresh list
                await this.fetchData();

            } catch (err) {
                this.error = err.message;
                console.error('Error creating item:', err);
            } finally {
                this.loading = false;
            }
        },

        /**
         * Update existing item
         */
        async updateItem(id, itemData) {
            this.loading = true;
            this.error = null;

            try {
                const response = await fetch(`/api/programs/${id}/`, {
                    method: 'PUT',
                    headers: {
                        'Content-Type': 'application/json',
                        'X-CSRFToken': this.getCookie('csrftoken')
                    },
                    body: JSON.stringify(itemData)
                });

                if (!response.ok) {
                    const errorData = await response.json();
                    throw new Error(JSON.stringify(errorData));
                }

                const data = await response.json();
                console.log('Updated item:', data);

                // Refresh list
                await this.fetchData();

            } catch (err) {
                this.error = err.message;
                console.error('Error updating item:', err);
            } finally {
                this.loading = false;
            }
        },

        /**
         * Delete item
         */
        async deleteItem(id) {
            if (!confirm('Are you sure you want to delete this item?')) {
                return;
            }

            this.loading = true;
            this.error = null;

            try {
                const response = await fetch(`/api/programs/${id}/`, {
                    method: 'DELETE',
                    headers: {
                        'Content-Type': 'application/json',
                        'X-CSRFToken': this.getCookie('csrftoken')
                    }
                });

                if (!response.ok) {
                    throw new Error(`HTTP error! status: ${response.status}`);
                }

                // Refresh list
                await this.fetchData();

            } catch (err) {
                this.error = err.message;
                console.error('Error deleting item:', err);
            } finally {
                this.loading = false;
            }
        },

        /**
         * Pagination
         */
        goToPage(page) {
            if (page < 1 || page > this.totalPages) {
                return;
            }
            this.currentPage = page;
            this.fetchData();
        },

        /**
         * Sorting
         */
        sortBy(field) {
            if (this.ordering === field) {
                this.ordering = `-${field}`;
            } else if (this.ordering === `-${field}`) {
                this.ordering = null;
            } else {
                this.ordering = field;
            }
            this.fetchData();
        },

        getSortIcon(field) {
            if (this.ordering === field) {
                return 'fas fa-sort-up';
            } else if (this.ordering === `-${field}`) {
                return 'fas fa-sort-down';
            }
            return 'fas fa-sort';
        },

        /**
         * Debounced search
         */
        debouncedSearch() {
            clearTimeout(this.debounceTimeout);
            this.debounceTimeout = setTimeout(() => {
                this.currentPage = 1;
                this.fetchData();
            }, 500);
        },

        /**
         * Get CSRF token from cookie
         */
        getCookie(name) {
            let cookieValue = null;
            if (document.cookie && document.cookie !== '') {
                const cookies = document.cookie.split(';');
                for (let i = 0; i < cookies.length; i++) {
                    const cookie = cookies[i].trim();
                    if (cookie.substring(0, name.length + 1) === (name + '=')) {
                        cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                        break;
                    }
                }
            }
            return cookieValue;
        },

        // Placeholder methods
        showCreateModal() {
            console.log('Show create modal');
        },

        editItem(item) {
            console.log('Edit item:', item);
        }
    }
};

// Export for use in other files
export default ExampleAPIComponent;
