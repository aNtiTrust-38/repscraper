document.addEventListener('DOMContentLoaded', function() {
    // Tab switching
    const tabs = document.querySelectorAll('.tab');
    const tabContents = document.querySelectorAll('.tab-content');
    tabs.forEach(tab => {
        tab.addEventListener('click', function() {
            tabs.forEach(t => t.classList.remove('active'));
            tabContents.forEach(tc => tc.classList.remove('active'));
            tab.classList.add('active');
            document.getElementById('tab-' + tab.dataset.tab).classList.add('active');
        });
    });

    const status = document.getElementById('form-status');
    const qualitySlider = document.getElementById('filters-quality-threshold');
    const qualityValue = document.getElementById('filters-quality-threshold-value');
    if (qualitySlider && qualityValue) {
        qualitySlider.addEventListener('input', function() {
            qualityValue.textContent = qualitySlider.value;
        });
    }

    // --- Form population helpers ---
    function setField(id, value) {
        const el = document.getElementById(id);
        if (!el) return;
        if (el.type === 'checkbox') {
            el.checked = !!value;
        } else if (el.type === 'range') {
            el.value = value ?? 0;
            if (el.id === 'filters-quality-threshold' && qualityValue) {
                qualityValue.textContent = value;
            }
        } else {
            el.value = value ?? '';
        }
    }
    function getField(id) {
        const el = document.getElementById(id);
        if (!el) return undefined;
        if (el.type === 'checkbox') {
            return el.checked;
        } else if (el.type === 'range') {
            return parseFloat(el.value);
        } else if (el.type === 'number') {
            return el.value === '' ? undefined : Number(el.value);
        } else {
            return el.value;
        }
    }
    function populateForm(config) {
        // Reddit
        setField('reddit-client-id', config.reddit?.client_id);
        setField('reddit-client-secret', config.reddit?.client_secret);
        setField('reddit-user-agent', config.reddit?.user_agent);
        setField('reddit-subreddits', (config.reddit?.subreddits || []).join(','));
        // Telegram
        setField('telegram-bot-token', config.telegram?.bot_token);
        setField('telegram-chat-id', config.telegram?.chat_id);
        setField('telegram-notification-format', config.telegram?.notification_format);
        // Scraping
        setField('scraping-batch-interval', config.scraping?.batch_interval_hours);
        setField('scraping-max-posts', config.scraping?.max_posts_per_batch);
        setField('scraping-enable-comments', config.scraping?.enable_comments);
        setField('scraping-monitor-new', config.scraping?.monitor_new_posts);
        setField('scraping-monitor-hot', config.scraping?.monitor_hot_posts);
        // Filters
        setField('filters-min-upvotes', config.filters?.min_upvotes);
        setField('filters-min-comments', config.filters?.min_comments);
        setField('filters-max-age', config.filters?.max_age_hours);
        setField('filters-quality-threshold', config.filters?.quality_threshold);
        setField('filters-exclude-deleted', config.filters?.exclude_deleted);
        setField('filters-exclude-removed', config.filters?.exclude_removed);
        // Platforms (only enabled is editable)
        setField('platform-taobao-enabled', config.platforms?.taobao?.enabled);
        setField('platform-weidian-enabled', config.platforms?.weidian?.enabled);
        setField('platform-1688-enabled', config.platforms?._1688?.enabled);
        setField('platform-yupoo-enabled', config.platforms?.yupoo?.enabled);
        setField('platform-others-enabled', config.platforms?.others?.enabled);
        setField('platform-pandabuy-enabled', config.platforms?.pandabuy?.enabled);
        // Jadeship
        setField('jadeship-enabled', config.jadeship?.enabled);
        setField('jadeship-api-url', config.jadeship?.api_url);
        setField('jadeship-timeout', config.jadeship?.timeout_seconds);
        setField('jadeship-retry', config.jadeship?.retry_attempts);
        setField('jadeship-default-agent', config.jadeship?.default_agent);
        // Database
        setField('database-url', config.database?.url);
        setField('database-backup-enabled', config.database?.backup_enabled);
        setField('database-backup-interval', config.database?.backup_interval_hours);
        setField('database-cleanup-old', config.database?.cleanup_old_data);
        setField('database-retention-days', config.database?.retention_days);
        // Health
        setField('health-enabled', config.health?.enabled);
        setField('health-telegram-alerts', config.health?.telegram_alerts);
        setField('health-discord-webhook', config.health?.discord_webhook);
        setField('health-pushbullet-token', config.health?.pushbullet_token);
        setField('health-check-interval', config.health?.check_interval_minutes);
        // Logging
        setField('logging-level', config.logging?.level);
        setField('logging-max-file-size', config.logging?.max_file_size_mb);
        setField('logging-backup-count', config.logging?.backup_count);
        setField('logging-console-output', config.logging?.console_output);
    }
    function gatherForm() {
        return {
            reddit: {
                client_id: getField('reddit-client-id'),
                client_secret: getField('reddit-client-secret'),
                user_agent: getField('reddit-user-agent'),
                subreddits: getField('reddit-subreddits').split(',').map(s => s.trim()).filter(Boolean)
            },
            telegram: {
                bot_token: getField('telegram-bot-token'),
                chat_id: getField('telegram-chat-id'),
                notification_format: getField('telegram-notification-format')
            },
            scraping: {
                batch_interval_hours: getField('scraping-batch-interval'),
                max_posts_per_batch: getField('scraping-max-posts'),
                enable_comments: getField('scraping-enable-comments'),
                monitor_new_posts: getField('scraping-monitor-new'),
                monitor_hot_posts: getField('scraping-monitor-hot')
            },
            filters: {
                min_upvotes: getField('filters-min-upvotes'),
                min_comments: getField('filters-min-comments'),
                max_age_hours: getField('filters-max-age'),
                quality_threshold: getField('filters-quality-threshold'),
                exclude_deleted: getField('filters-exclude-deleted'),
                exclude_removed: getField('filters-exclude-removed')
            },
            platforms: {
                taobao: {priority: 1, enabled: getField('platform-taobao-enabled'), weight: 0.4},
                weidian: {priority: 2, enabled: getField('platform-weidian-enabled'), weight: 0.25},
                _1688: {priority: 3, enabled: getField('platform-1688-enabled'), weight: 0.2},
                yupoo: {priority: 4, enabled: getField('platform-yupoo-enabled'), weight: 0.1},
                others: {priority: 5, enabled: getField('platform-others-enabled'), weight: 0.04},
                pandabuy: {priority: 6, enabled: getField('platform-pandabuy-enabled'), weight: 0.01}
            },
            jadeship: {
                enabled: getField('jadeship-enabled'),
                api_url: getField('jadeship-api-url'),
                timeout_seconds: getField('jadeship-timeout'),
                retry_attempts: getField('jadeship-retry'),
                default_agent: getField('jadeship-default-agent'),
                agent_priority: [
                    'allchinabuy', 'cnfans', 'mulebuy', 'wegobuy', 'sugargoo', 'cssbuy', 'superbuy', 'pandabuy'
                ] // fixed order
            },
            database: {
                url: getField('database-url'),
                backup_enabled: getField('database-backup-enabled'),
                backup_interval_hours: getField('database-backup-interval'),
                cleanup_old_data: getField('database-cleanup-old'),
                retention_days: getField('database-retention-days')
            },
            health: {
                enabled: getField('health-enabled'),
                telegram_alerts: getField('health-telegram-alerts'),
                discord_webhook: getField('health-discord-webhook'),
                pushbullet_token: getField('health-pushbullet-token'),
                check_interval_minutes: getField('health-check-interval')
            },
            logging: {
                level: getField('logging-level'),
                max_file_size_mb: getField('logging-max-file-size'),
                backup_count: getField('logging-backup-count'),
                console_output: getField('logging-console-output')
            }
        };
    }

    // --- Fetch config on load ---
    function loadConfigOrDefaults() {
        fetch('/config')
            .then(r => r.json())
            .then(data => {
                populateForm(data);
                status.textContent = 'Loaded config.';
            })
            .catch(() => {
                fetch('/config/defaults')
                    .then(r => r.json())
                    .then(data => {
                        populateForm(data);
                        status.textContent = 'Loaded defaults.';
                    });
            });
    }
    loadConfigOrDefaults();

    // --- Save config ---
    document.getElementById('save-btn').addEventListener('click', function() {
        const config = gatherForm();
        status.textContent = 'Saving...';
        fetch('/config', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify(config)
        })
        .then(async r => {
            const data = await r.json();
            if (r.status === 422) {
                // Validation error: highlight fields and show details
                status.textContent = (data.error || 'Validation failed.') + (data.fields ? ' (' + data.fields.map(f => f.loc.join('.') + ': ' + f.msg).join('; ') + ')' : '');
                // Optionally, highlight fields with errors
                if (data.fields) {
                    data.fields.forEach(f => {
                        const fieldId = fieldLocToId(f.loc);
                        if (fieldId) {
                            const el = document.getElementById(fieldId);
                            if (el) el.classList.add('input-error');
                        }
                    });
                }
            } else if (data.success) {
                status.textContent = 'Saved successfully!';
            } else {
                status.textContent = 'Save failed: ' + (data.detail || data.error || 'Unknown error');
            }
        })
        .catch(e => {
            status.textContent = 'Save failed: ' + e;
        });
    });

    // Helper: map Pydantic error loc to field id
    function fieldLocToId(loc) {
        // Example loc: ['reddit', 'client_id'] => 'reddit-client-id'
        if (!Array.isArray(loc)) return null;
        return loc.join('-').replace(/_/g, '-');
    }

    // --- Load defaults ---
    document.getElementById('defaults-btn').addEventListener('click', function() {
        fetch('/config/defaults')
            .then(r => r.json())
            .then(data => {
                populateForm(data);
                status.textContent = 'Loaded defaults.';
            });
    });

    // --- Test config (validate) ---
    document.getElementById('test-btn').addEventListener('click', function() {
        const config = gatherForm();
        status.textContent = 'Validating...';
        fetch('/config/validate', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify(config)
        })
        .then(r => r.json())
        .then(data => {
            if (data.valid) {
                status.textContent = 'Validation passed!';
            } else {
                status.textContent = 'Validation failed: ' + (data.errors?.map(e => e.loc.join('.') + ': ' + e.msg).join('; ') || 'Unknown error');
            }
        })
        .catch(e => {
            status.textContent = 'Validation failed: ' + e;
        });
    });
}); 