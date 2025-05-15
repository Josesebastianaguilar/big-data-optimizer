"use client";

import { useState } from "react";
import Link from "next/link";
import Header from "@/components/Header";
import Footer from "@/components/Footer";
import { FaArrowLeft, FaPlus } from "react-icons/fa";

// Mock repository data (replace with real fetch)
const repository = {
  _id: 1,
  name: "Repository A",
  version: "1.0.0",
  parameters: [
    { name: "status", type: "string" },
    { name: "amount", type: "number" },
    { name: "category", type: "string" },
    { name: "score", type: "number" },
  ],
};

const ACTIONS = [
  { key: "filter", label: "Filter" },
  { key: "group", label: "Group" },
  { key: "aggregation", label: "Aggregation" },
];

const FILTER_OPERATORS = [
  { key: "===", label: "Equals", types: ["string", "number"] },
  { key: "!==", label: "Not Equals", types: ["string", "number"] },
  { key: ">", label: "Greater Than", types: ["number"] },
  { key: "<", label: "Lower Than", types: ["number"] },
  { key: ">=", label: "Greater or Equal", types: ["number"] },
  { key: "<=", label: "Lower or Equal", types: ["number"] },
  { key: "contains", label: "Contains", types: ["string"] },
];

const AGGREGATION_OPERATIONS = [
  "sum", "min", "max", "mean", "count", "median", "standard deviation", "variance", "first", "last", "unique", "mode", "range"
];

export default function CreateProcessPage() {
  // State for selected actions (order matters: filter always first if selected)
  const [selectedActions, setSelectedActions] = useState([]);
  // State for action parameters
  const [actionParams, setActionParams] = useState({
    filter: [],
    group: [],
    aggregation: [],
  });

  // Handle action selection
  const handleActionChange = (actionKey, checked) => {
    let next = [...selectedActions];
    if (checked) {
      if (!next.includes(actionKey)) next.push(actionKey);
    } else {
      next = next.filter((a) => a !== actionKey);
    }
    // Filter always first if present
    if (next.includes("filter")) {
      next = ["filter", ...next.filter((a) => a !== "filter")];
    }
    setSelectedActions(next);
  };

  // Handle filter param change
  const handleFilterParamChange = (idx, field, value) => {
    setActionParams((prev) => {
      const next = [...prev.filter];
      let updated = { ...next[idx], [field]: value };

      if (field === "param") {
        const paramType = repository.parameters.find((p) => p.name === value)?.type;
        const currentOperator = updated.operator;
        // If current operator is not valid for new type, reset it
        if (
          currentOperator &&
          !FILTER_OPERATORS.find(
            (op) => op.key === currentOperator && op.types.includes(paramType)
          )
        ) {
          updated.operator = "";
        }
        // Optionally reset value as well
        updated.value = "";
      }

      next[idx] = updated;
      return { ...prev, filter: next };
    });
  };

  // Add/remove filter condition
  const addFilterCondition = () => {
    setActionParams((prev) => ({
      ...prev,
      filter: [...prev.filter, { param: "", operator: "", value: "" }],
    }));
  };
  const removeFilterCondition = (idx) => {
    setActionParams((prev) => ({
      ...prev,
      filter: prev.filter.filter((_, i) => i !== idx),
    }));
  };

  // Handle group param change
  const handleGroupParamsChange = (params) => {
    setActionParams((prev) => ({ ...prev, group: params }));
  };

  // Handle aggregation param change
  const handleAggregationParamChange = (idx, field, value) => {
    setActionParams((prev) => {
      const next = [...prev.aggregation];
      next[idx] = { ...next[idx], [field]: value };
      return { ...prev, aggregation: next };
    });
  };
  const addAggregationParam = () => {
    setActionParams((prev) => ({
      ...prev,
      aggregation: [...prev.aggregation, { param: "", operation: "" }],
    }));
  };
  const removeAggregationParam = (idx) => {
    setActionParams((prev) => ({
      ...prev,
      aggregation: prev.aggregation.filter((_, i) => i !== idx),
    }));
  };

  // Handle form submit
  const handleSubmit = (e) => {
    e.preventDefault();
    // TODO: Send to backend
    alert(JSON.stringify({ actions: selectedActions, params: actionParams }, null, 2));
  };

  // Helper: get available parameters by type
  const getParamsByType = (type) =>
    repository.parameters.filter((p) => p.type === type);

  // Helper: get available parameters for aggregation (number only)
  const numberParams = getParamsByType("number");

  const isFormValid = () => {
    // At least one action
    if (selectedActions.length === 0) return false;

    // Filter validation
    if (selectedActions.includes("filter")) {
      if (actionParams.filter.length === 0) return false;
      for (const cond of actionParams.filter) {
        // Must have param and operator
        if (!cond.param || !cond.operator) return false;
        const paramType = repository.parameters.find((p) => p.name === cond.param)?.type;
        // For string param and equality/inequality, value must be empty string
        if (
          paramType === "string" &&
          (cond.operator === "===" || cond.operator === "!==")
        ) {
          if (cond.value !== "") return false;
        } else {
          // For all other cases, value must be set (not empty)
          if (cond.value === "" || cond.value === undefined || cond.value === null) return false;
        }
      }
    }

    // Group validation
    if (selectedActions.includes("group")) {
      if (!Array.isArray(actionParams.group) || actionParams.group.length === 0) return false;
    }

    // Aggregation validation
    if (selectedActions.includes("aggregation")) {
      if (actionParams.aggregation.length === 0) return false;
      for (const agg of actionParams.aggregation) {
        if (!agg.param || !agg.operation) return false;
      }
    }

    return true;
  };

  return (
    <div className="min-h-screen flex flex-col bg-gray-50 text-gray-800">
      <Header backgroundColor="bg-orange-500" title="Create Process" />
      <main className="flex-grow max-w-2xl mx-auto w-full px-4 py-8">
        <div className="flex justify-end items-center mb-2">    
          <Link
            title="Go Back"
            href={`/processes?repository=${repository._id}`}
            className="inline-block bg-orange-500 text-white py-2 px-4 rounded-md hover:bg-orange-600 focus:outline-none focus:ring-2 focus:ring-orange-600 focus:ring-offset-2"
          >
            <FaArrowLeft className="w-4 h-4" />
          </Link>
        </div>
        <div className="bg-white rounded-lg shadow p-6 mb-6">
          <h2 className="text-xl font-bold mb-2">Repository Info</h2>
          <div className="mb-2"><strong>Name:</strong> {repository.name}</div>
          <div className="mb-2"><strong>ID:</strong> {repository._id}</div>
          <div className="mb-2"><strong>Version:</strong> {repository.version}</div>
        </div>
        <div className="bg-white rounded-lg shadow p-6">
          <h2 className="text-xl font-bold mb-4">Configure Process</h2>
          <form onSubmit={handleSubmit} className="space-y-6">
            {/* Action selection */}
            <div>
              <label className="block font-semibold mb-2">Select Actions (1-3):</label>
              <div className="flex gap-4">
                {ACTIONS.map((action) => (
                  <label key={action.key} className="flex items-center gap-1 cursor-pointer">
                    <input
                      type="checkbox"
                      className="cursor-pointer"
                      checked={selectedActions.includes(action.key)}
                      onChange={(e) => handleActionChange(action.key, e.target.checked)}
                      disabled={
                        !selectedActions.includes(action.key) &&
                        selectedActions.length >= 3
                      }
                    />
                    {action.label}
                  </label>
                ))}
              </div>
            </div>

            {/* Filter action */}
            {selectedActions.includes("filter") && (
              <div className="border rounded p-4 bg-orange-50">
                <div className="font-semibold mb-2">Filter Conditions</div>
                {actionParams.filter.length === 0 && (
                  <button
                    type="button"
                    className=" cursor-pointer bg-orange-500 text-white px-3 py-1 rounded mb-2"
                    onClick={addFilterCondition}
                  >
                    Add Filter Condition
                  </button>
                )}
                {actionParams.filter.map((cond, idx) => {
                  // Get param type for operator filtering
                  const paramType =
                    repository.parameters.find((p) => p.name === cond.param)?.type || "";
                  return (
                    <div key={idx} className="flex gap-2 items-center mb-2">
                      <select
                        className="cursor-pointer border rounded px-2 py-1"
                        value={cond.param}
                        onChange={(e) =>
                          handleFilterParamChange(idx, "param", e.target.value)
                        }
                        required
                      >
                        <option value="">Parameter</option>
                        {repository.parameters.map((p) => (
                          <option key={p.name} value={p.name}>
                            {p.name}
                          </option>
                        ))}
                      </select>
                      <select
                        className="cursor-pointer border rounded px-2 py-1"
                        value={cond.operator}
                        onChange={(e) =>
                          handleFilterParamChange(idx, "operator", e.target.value)
                        }
                        required
                        disabled={!cond.param}
                      >
                        <option value="">Operator</option>
                        {FILTER_OPERATORS.filter((op) =>
                          paramType ? op.types.includes(paramType) : true
                        ).map((op) => (
                          <option key={op.key} value={op.key}>
                            {op.label}
                          </option>
                        ))}
                      </select>
                      <input
                        className="cursor-pointer border rounded px-2 py-1"
                        type={paramType === "number" ? "number" : "text"}
                        value={cond.value}
                        onChange={(e) =>
                          handleFilterParamChange(idx, "value", e.target.value)
                        }
                        placeholder="Value"
                        required={paramType !== 'string' && cond.operator !== "===" && cond.operator !== "!=="}
                        disabled={!cond.operator}
                      />
                      <button
                        type="button"
                        className="cursor-pointer text-red-600 font-bold px-2"
                        onClick={() => removeFilterCondition(idx)}
                      >
                        ×
                      </button>
                    </div>
                  );
                })}
                {actionParams.filter.length > 0 && (
                  <button
                    type="button"
                    className="cursor-pointer bg-orange-500 text-white px-3 py-1 rounded"
                    onClick={addFilterCondition}
                  >
                    Add Another Condition
                  </button>
                )}
              </div>
            )}

            {/* Group action */}
            {selectedActions.includes("group") && (
              <div className="border rounded p-4 bg-orange-50">
                <div className="font-semibold mb-2">Group By Parameters</div>
                <div className="flex flex-wrap gap-3">
                  {repository.parameters.map((param) => (
                    <label key={param.name} className="flex items-center gap-1 cursor-pointer">
                      <input
                        type="checkbox"
                        className="cursor-pointer"
                        checked={actionParams.group.includes(param.name)}
                        onChange={(e) => {
                          const next = e.target.checked
                            ? [...actionParams.group, param.name]
                            : actionParams.group.filter((p) => p !== param.name);
                          handleGroupParamsChange(next);
                        }}
                      />
                      {param.name}
                    </label>
                  ))}
                </div>
                {actionParams.group.length === 0 && (
                  <div className="text-red-600 text-sm mt-2">Select at least one parameter.</div>
                )}
              </div>
            )}

            {/* Aggregation action */}
            {selectedActions.includes("aggregation") && (
              <div className="border rounded p-4 bg-orange-50">
                <div className="font-semibold mb-2">Aggregation</div>
                {actionParams.aggregation.length === 0 && (
                  <button
                    type="button"
                    className="cursor-pointer bg-orange-500 text-white px-3 py-1 rounded mb-2"
                    onClick={addAggregationParam}
                  >
                    Add Aggregation
                  </button>
                )}
                {actionParams.aggregation.map((agg, idx) => (
                  <div key={idx} className="flex gap-2 items-center mb-2">
                    <select
                      className="cursor-pointer border rounded px-2 py-1"
                      value={agg.param}
                      onChange={(e) =>
                        handleAggregationParamChange(idx, "param", e.target.value)
                      }
                      required
                    >
                      <option value="">Parameter</option>
                      {numberParams.map((p) => (
                        <option key={p.name} value={p.name}>
                          {p.name}
                        </option>
                      ))}
                    </select>
                    <select
                      className="cursor-pointer border rounded px-2 py-1"
                      value={agg.operation}
                      onChange={(e) =>
                        handleAggregationParamChange(idx, "operation", e.target.value)
                      }
                      required
                      disabled={!agg.param}
                    >
                      <option value="">Operation</option>
                      {AGGREGATION_OPERATIONS.map((op) => (
                        <option key={op} value={op}>
                          {op}
                        </option>
                      ))}
                    </select>
                    <button
                      type="button"
                      className="cursor-pointer text-red-600 font-bold px-2"
                      onClick={() => removeAggregationParam(idx)}
                    >
                      ×
                    </button>
                  </div>
                ))}
                {actionParams.aggregation.length > 0 && (
                  <button
                    type="button"
                    className="cursor-pointer bg-orange-500 text-white px-3 py-1 rounded"
                    onClick={addAggregationParam}
                  >
                    Add Another Aggregation
                  </button>
                )}
                {numberParams.length === 0 && (
                  <div className="text-red-600 text-sm mt-2">No numeric parameters available for aggregation.</div>
                )}
              </div>
            )}

            <button
              type="submit"
              className={`cursor-pointer bg-orange-500 text-white py-2 px-4 rounded ${isFormValid() ? "hover:bg-orange-600" : "opacity-50 cursor-not-allowed"}`}
              disabled={!isFormValid()}
            >
              <FaPlus className="inline mr-2" />
              Create Process
            </button>
          </form>
        </div>
      </main>
      <Footer backgroundColor="bg-orange-500" />
    </div>
  );
}
