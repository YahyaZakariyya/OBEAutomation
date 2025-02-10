export const SelectSection = {
    props: ["sections", "modelValue"],
    emits: ["update:modelValue"],
    template: `
        <div class="form-group">
            <label for="section">Section</label>
            <select id="section" class="form-control" @change="$emit('update:modelValue', $event.target.value)">
                <option value="">-- Select Section --</option>
                <option v-for="section in sections" :key="section.id" :value="section.id">
                    {{ section.name || 'Section ' + section.id }}
                </option>
            </select>
        </div>
    `
};