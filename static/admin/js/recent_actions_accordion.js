(function() {
    'use strict';

    /**
     * Recent Actions Accordion Handler
     * Manages expand/collapse state with accessibility support
     */
    const RecentActionsAccordion = {
        init() {
            this.toggle = document.querySelector('.recent-actions-toggle');
            this.content = document.querySelector('#recent-actions-content');

            if (!this.toggle || !this.content) {
                return;
            }

            this.attachEventListeners();
            this.restoreState();
        },

        attachEventListeners() {
            this.toggle.addEventListener('click', () => this.handleToggle());
            this.toggle.addEventListener('keydown', (e) => {
                if (e.key === 'Enter' || e.key === ' ') {
                    e.preventDefault();
                    this.handleToggle();
                }
            });
        },

        handleToggle() {
            const isExpanded = this.toggle.getAttribute('aria-expanded') === 'true';
            this.setExpanded(!isExpanded);
        },

        setExpanded(expanded) {
            this.toggle.setAttribute('aria-expanded', String(expanded));
            
            if (expanded) {
                this.content.removeAttribute('hidden');
            } else {
                this.content.setAttribute('hidden', '');
            }

            localStorage.setItem('admin-recent-actions-expanded', String(expanded));
        },

        restoreState() {
            const saved = localStorage.getItem('admin-recent-actions-expanded');
            const shouldExpand = saved === 'true';
            this.setExpanded(shouldExpand);
        }
    };

    // Initialize when DOM is ready
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', () => RecentActionsAccordion.init());
    } else {
        RecentActionsAccordion.init();
    }
})();
