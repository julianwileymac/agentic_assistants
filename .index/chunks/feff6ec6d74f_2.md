# Chunk: feff6ec6d74f_2

- source: `.venv-lab/Lib/site-packages/notebook/static/1871.c375ee093b7e51966390.js`
- lines: 140-202
- chunk: 3/78

```
               item,
            };
        });
}
/** Converts `KeyedFormDataType` data into the inner `formData`
 *
 * @param keyedFormData - The `KeyedFormDataType` to be converted
 * @returns - The inner `formData` item(s) in the `keyedFormData`
 */
function keyedToPlainFormData(keyedFormData) {
    if (Array.isArray(keyedFormData)) {
        return keyedFormData.map((keyedItem) => keyedItem.item);
    }
    return [];
}
/** The `ArrayField` component is used to render a field in the schema that is of type `array`. It supports both normal
 * and fixed array, allowing user to add and remove elements from the array data.
 */
class ArrayField extends index_js_.Component {
    /** Constructs an `ArrayField` from the `props`, generating the initial keyed data from the `formData`
     *
     * @param props - The `FieldProps` for this template
     */
    constructor(props) {
        super(props);
        /** Returns the default form information for an item based on the schema for that item. Deals with the possibility
         * that the schema is fixed and allows additional items.
         */
        this._getNewFormDataRow = () => {
            const { schema, registry } = this.props;
            const { schemaUtils } = registry;
            let itemSchema = schema.items;
            if ((0,lib_index_js_.isFixedItems)(schema) && (0,lib_index_js_.allowAdditionalItems)(schema)) {
                itemSchema = schema.additionalItems;
            }
            // Cast this as a T to work around schema utils being for T[] caused by the FieldProps<T[], S, F> call on the class
            return schemaUtils.getDefaultFormState(itemSchema);
        };
        /** Callback handler for when the user clicks on the add button. Creates a new row of keyed form data at the end of
         * the list, adding it into the state, and then returning `onChange()` with the plain form data converted from the
         * keyed data
         *
         * @param event - The event for the click
         */
        this.onAddClick = (event) => {
            this._handleAddClick(event);
        };
        /** Callback handler for when the user clicks on the add button on an existing array element. Creates a new row of
         * keyed form data inserted at the `index`, adding it into the state, and then returning `onChange()` with the plain
         * form data converted from the keyed data
         *
         * @param index - The index at which the add button is clicked
         */
        this.onAddIndexClick = (index) => {
            return (event) => {
                this._handleAddClick(event, index);
            };
        };
        /** Callback handler for when the user clicks on the copy button on an existing array element. Clones the row of
         * keyed form data at the `index` into the next position in the state, and then returning `onChange()` with the plain
         * form data converted from the keyed data
         *
```
